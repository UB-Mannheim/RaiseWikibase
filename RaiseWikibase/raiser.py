from RaiseWikibase.dbconnection import DBConnection
from RaiseWikibase.datamodel import namespaces
from RaiseWikibase.utils import get_ip, execute_shell
from RaiseWikibase.settings import Settings
import uuid
import json
from tqdm import tqdm


ip = get_ip()


def page(connection=None, content_model=None, namespace=None, text=None, page_title=None, new=None):
    """
    It executes inserts into multiple tables in MariaDB, but does not commit them.

    :param dbconnection.DBConnection connection: Connection object to MariaDB
    :param str content_model: Content model of a page
    :param str namespace: Namespace of a page (see "https://www.mediawiki.org/wiki/Extension_default_namespaces")
    :param text: Text of a page
    :type text: str for texts or dict for entities
    :param str page_title: Title of a page without namespace.
    :param bool new: True, if a new page is created. False, if a page is changed.
    :raises ValueError: if entity type (inferred from content model) is not valid
    :raises ValueError: if namespace for the chosen content model is not valid
    :raises ValueError: if content model is not valid
    :raises ValueError: if page title is not specified
    """
    # 1. Check whether the content_model is valid.
    if content_model in ['wikibase-item', 'wikibase-property', 'wikibase-lexeme']:
        # 2.1 Take labels, descriptions and aliases from text for the secondary tables
        fingerprint = {}
        fingerprint['label'] = text.get('labels')
        fingerprint['description'] = text.get('descriptions')
        fingerprint['alias'] = text.get('aliases')
        # 2.2 For structured data find the namespace, etype (entity type), eid
        # and page_title. Convert text from dict to str.
        namespace = namespaces[content_model]
        etype = content_model.replace('wikibase-', '')
        if etype == 'property':
            prefix = "P"
        elif etype == 'item':
            prefix = "Q"
        elif etype == 'lexeme':
            prefix = "L"
        else:
            raise ValueError('{} is not a valid entity type. Try "property" or "item".'.format(etype))
        if new:
            new_eid = str(connection.get_last_eid(content_model=content_model) + 1)
            text['id'] = prefix + new_eid
        page_title = text['id']
        for value in text['claims'].values():
            [val.update({'id': text['id'] + '$' + str(uuid.uuid4())}) for val in value]
        text = json.dumps(text, separators=(',', ':'))
    elif content_model in ['wikitext', 'Scribunto', 'sanitized-css']:
        # 3. For unstructured data check whether the namespace is valid and set
        # page_title.
        if namespace is None:
            raise ValueError('{} is not a valid namespace for the content model {}.'.format(namespace, content_model))
        if page_title is None:
            raise ValueError('{} is not a valid "page_title".'.format(page_title))
    else:
        raise ValueError('{} is not a valid "content_model". Do we need to add it?'.format(content_model))

    # 4. Escape text.
    # text = re.escape(text)
    # text = text.replace("\'", "''")
    
    # 5. Find all IDs in different tables.
    [text_id, page_id, comment_id, content_id, rev_id] = connection.get_ids(new=new, page_title=page_title,
                                                                            namespace=namespace)
    model_id = connection.model_ids.get(content_model)

    # 6. Insert data.
    connection.insert(text_id=text_id, text=text, page_id=page_id,
                          page_title=page_title, comment_id=comment_id,
                          content_id=content_id, model_id=model_id,
                          content_model=content_model, namespace=namespace,
                          rev_id=rev_id, new=new, ip=ip)
    # 7. Insert fingerprint (labels, descriptions & aliases) into the secondary tables.
    if content_model in ['wikibase-item', 'wikibase-property']:
        connection.insert_secondary(fingerprint=fingerprint, new_eid=new_eid,
                                    content_model=content_model)
    # For structured data update counters in 'wb_id_counters'-table.
    if new and (content_model in ['wikibase-item', 'wikibase-property', 'wikibase-lexeme']):
        connection.update_wb_id_counters(new_eid=new_eid, content_model=content_model)


def batch(content_model=None, texts=None, namespace=None, page_title=None, new=True):
    """
    It commits batch inserts into MariaDB.

    :param str content_model: Content model of a page
    :param str namespace: Namespace of a page (see "https://www.mediawiki.org/wiki/Extension_default_namespaces")
    :param texts: Texts of pages
    :type texts: list or tuple of strings (wikitexts) or dictionaries (entities)
    :param str page_title: Title of a page without namespace.
    :param bool new: True, if a new page is created. False, if a page is changed.
    """
    if not page_title:
        page_title = [None for pt in range(0,len(texts))]
    try:
        connection = DBConnection()
        for ind, (text, pt) in enumerate(tqdm(zip(texts, page_title))):
            page(connection=connection, content_model=content_model,
                 namespace=namespace, text=text, page_title=pt, new=new)
        connection.conn.commit()
        connection.conn.close()
    except connection.conn.error() as error:
        print("Failed to update: {}".format(error))
        # reverting changes because of exception
        connection.conn.rollback()
    finally:
        # closing database connection.
        if connection.conn.open:
            connection.conn.close()


def create_bot(bot_name='bot'):
    """
    Creates login and password for a bot. Saves them to '.config.json'.
    If bot exists, it prints about it.
    If bot has been created, it prints where the metadata is saved.
    """
    connection = DBConnection()
    connection.bot_delete()
    botuser, botpass = connection.bot_create(bot_name)
    if botpass is None:
        print("Bot already exists.")
        sys.exit(1)

    with Settings() as config:
        config.username = botuser
        config.password = botpass
        config.mediawiki_api_url = "http://localhost:8181/w/api.php"
        config.sparql_endpoint_url = "http://localhost:8989/bigdata/sparql"
        config.wikibase_url = "http://localhost:8181"

    print("Bot is created. Metadata is saved to '.config.json'.")


def building_indexing():
    """Builds the ElasticSearch index"""
    connection = DBConnection()
    container = connection.docker_wikibase
    connection.conn.close()

    # CirrusSearch indexing. For huge tables use parallelization as explained at
    # https://github.com/wikimedia/mediawiki-extensions-CirrusSearch/blob/master/README
    execute_shell(
        'docker exec ' +
        container +
        ' bash "-c" "php extensions/CirrusSearch/maintenance/ForceSearchIndex.php --skipLinks --indexOnSkip"')
    execute_shell(
        'docker exec ' +
        container +
        ' bash "-c" "php extensions/CirrusSearch/maintenance/ForceSearchIndex.php --skipParse"')
    # Run runJobs.php after CirrusSearch indexing. See https://www.mediawiki.org/wiki/Manual:RunJobs.php
    execute_shell(
        'docker exec ' +
        container +
        ' bash "-c" "php maintenance/runJobs.php"')