import hashlib
import os
import random
import string
import MySQLdb
from RaiseWikibase.docker import docker_names, docker_env, docker_ports
from RaiseWikibase.mwbot import MWBot
import re
import datetime


class DBConnection:
    def __init__(self):
        [self.docker_mysql, self.docker_wikibase] = docker_names()
        self.mysql_env = docker_env(self.docker_mysql)
        self.mysql_ports = docker_ports(self.docker_mysql)
        self.wikibase_env = docker_env(self.docker_wikibase)
        self.conn = self.mysql_connect()
        self.user_id = self.get_admin_user_id()
        self.create_content_models()
        self.model_ids = self.get_content_models()
        self.create_wbt_types()
        self.wbt_types = self.get_wbt_types()
        self.MWBot = MWBot()

    def mysql_connect(self):
        """Helper function connecting to SQL database."""
        conn = MySQLdb.connect(
            database=self.mysql_env["MYSQL_DATABASE"],
            user=self.mysql_env["MYSQL_USER"],
            password=self.mysql_env["MYSQL_PASSWORD"],
            host=self.mysql_ports["3306/tcp"][0]["HostIp"],
            port=int(self.mysql_ports["3306/tcp"][0]["HostPort"])
        )
        conn.autocommit = False
        conn.charset = 'utf-8'
        return conn

    def get_admin_user_id(self):
        """Helper function for retrieving primary admin user id."""
        cur = self.conn.cursor()
        cur.execute("SELECT user_id FROM user WHERE user_name = '%s'" \
                    % self.wikibase_env["MW_ADMIN_NAME"])
        out = cur.fetchone()[0]
        cur.close()
        return out

    def bot_create(self, name, password=None, salt=None, token=None):
        """Creates a bot with a random or given password. Returns the
        password."""
        fullname = '%s@%s' % (self.wikibase_env["MW_ADMIN_NAME"], name)
        cur = self.conn.cursor()
        if self.bot_exists(name):
            return (fullname, None)
        if password is None:
            # 'random' password is actually a string in base32 encoding of
            # length 32
            password = ''.join([
                random.choice(string.ascii_lowercase[:22] + string.digits)
                for i in range(32)
            ])
        if token is None:
            token = hashlib.md5(os.urandom(16)).hexdigest()
        query = """INSERT INTO bot_passwords VALUES ({bp_user}, '{bp_app_id}',
        '{bp_password}', '{bp_token}', '{bp_restrictions}',
        '{bp_grants}')""".format(
            bp_user=self.user_id,
            bp_app_id=name,
            bp_password=self.MWBot.gen_password(password, salt),
            bp_token=token,
            bp_restrictions=self.MWBot.get_ips(),
            bp_grants=self.MWBot.get_perms(),
        )
        cur.execute(query)
        self.conn.commit()
        cur.close()
        return (fullname, password)

    def bot_delete(self, name=None):
        """Deletes bot matching name (or all if no name was given)."""
        cur = self.conn.cursor()
        query = "DELETE FROM bot_passwords"
        if not name is None:
            query += " WHERE bp_app_id = '%s'" % name
        cur.execute(query)
        self.conn.commit()
        cur.close()

    def bot_exists(self, name):
        """Returns True if bot with given name exists, False otherwise."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM bot_passwords WHERE bp_user = %d AND" \
                    " bp_app_id = '%s'" % (self.user_id, name))
        out = True if len(cur.fetchall()) != 0 else False
        cur.close()
        return out

    def bot_list(self):
        """Returns a list of all bots."""
        ret = []
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM bot_passwords")
        for row in cur.fetchall():
            ret.append(row)
        cur.close()
        return ret

    def bot_schema(self):
        """Returns a tuple containing the names of the bot table columns."""
        cur = self.conn.cursor()
        cur.execute("DESCRIBE bot_passwords")
        out = tuple(i[0] for i in cur.fetchall())
        cur.close()
        return out

    def create_wbt_types(self):
        """Creates three wbt_types: label, description and alias"""
        cur = self.conn.cursor()
        q = "INSERT IGNORE INTO wbt_type (wby_name ) VALUES('label'),('description'),('alias')"
        cur.execute(q)
        self.conn.commit()
        cur.close()

    def get_wbt_types(self):
        """Returns the existing wbt_types from wbt_type-table"""
        cur = self.conn.cursor()
        q = "SELECT * FROM wbt_type"
        cur.execute(q)
        out = dict((y.decode('utf-8'), x) for x, y in cur.fetchall())
        self.conn.commit()
        cur.close()
        return out

    def create_content_models(self):
        """Creates a few content models"""
        cur = self.conn.cursor()
        q = "INSERT IGNORE INTO content_models (model_name ) VALUES('wikibase-item'),('wikibase-property'),('wikibase-lexeme'),('Scribunto'),('sanitized-css')"
        cur.execute(q)
        self.conn.commit()
        cur.close()

    def get_content_models(self):
        """Returns the existing content models from content_models-table"""
        cur = self.conn.cursor()
        q = "SELECT * FROM content_models"
        cur.execute(q)
        out = dict((y.decode('utf-8'), x) for x, y in cur.fetchall())
        self.conn.commit()
        cur.close()
        return out

    def get_last_eid(self, content_model=None):
        """Returns the last entity ID (int) for the given content_model.
        If wb_id_counters-table has no counters for the given content_model,
        then sets the last entity ID to zero."""
        cur = self.conn.cursor()
        try:
            q0 = "SELECT id_type FROM wb_id_counters WHERE id_type='{db_content_model}'".format(
                db_content_model=content_model)
            cur.execute(q0)
            counters = cur.fetchone()[0]
            if counters == content_model.encode('UTF-8'):
                q = """SELECT id_value AS next_id from wb_id_counters where id_type='{db_content_model}'""".format(
                    db_content_model=content_model)
                cur.execute(q)
                eid = cur.fetchone()[0]
        except Exception:
            eid = 0
        cur.close()
        return eid

    def get_text_id(self):
        """Returns the last text_id (int) in text-table"""
        cur = self.conn.cursor()
        q = "SELECT max(old_id) FROM text"
        cur.execute(q)
        text_id = cur.fetchone()[0]
        cur.close()
        return text_id

    def get_page_id(self):
        """Returns the last page_id (int) in page-table"""
        cur = self.conn.cursor()
        q = "SELECT max(page_id) FROM page"
        cur.execute(q)
        page_id = cur.fetchone()[0]
        cur.close()
        return page_id

    def get_rev_id(self):
        """Returns the last revision_id (int) in revision-table"""
        cur = self.conn.cursor()
        q = "SELECT max(rev_id) FROM revision"
        cur.execute(q)
        page_id = cur.fetchone()[0]
        cur.close()
        return page_id

    def get_comment_id(self):
        """Returns the last comment_id (int) in comment-table"""
        cur = self.conn.cursor()
        q = "SELECT max(comment_id) FROM comment"
        cur.execute(q)
        comment_id = cur.fetchone()[0]
        cur.close()
        return comment_id

    def get_content_id(self):
        """Returns the last content_id (int) in content-table"""
        cur = self.conn.cursor()
        q = "SELECT max(content_id) FROM content"
        cur.execute(q)
        content_id = cur.fetchone()[0]
        cur.close()
        return content_id

    def get_wbtl_id(self, cur=None, wbtl_type_id=None, wbxl_language=None, wbx_text=None, wbxl_id=None):
        """Returns wbtl_id (int) in wbt_term_in_lang-table for given wbtl_type_id (int),
        wbxl_language (language code), wbx_text (str) and wbxl_id (int)"""
        try:
            cur.execute("""SELECT wbtl_id FROM wbt_term_in_lang, wbt_text_in_lang,
                    wbt_text WHERE wbtl_text_in_lang_id=wbxl_id AND wbtl_type_id=%s
                    AND wbxl_language=%s AND wbxl_text_id=wbx_id AND wbx_text=%s""",
                    [wbtl_type_id, wbxl_language, wbx_text])
            wbtl_id = cur.fetchone()[0]
        except Exception:
            cur.execute("INSERT INTO wbt_term_in_lang VALUES(NULL,%s,%s)", [wbtl_type_id, wbxl_id])
            cur.execute("SELECT LAST_INSERT_ID()")
            wbtl_id = cur.fetchone()[0]
        return wbtl_id

    def get_wbxl_id(self, cur=None, wbxl_language=None, wbx_text=None, wbx_id=None):
        """Returns wbxl_id (int) in wbt_text_in_lang-table for given
        wbxl_language (language code), wbx_text (str) and wbx_id (int)"""
        try:
            cur.execute("""SELECT wbxl_id FROM wbt_text_in_lang, wbt_text
                    WHERE wbxl_language=%s AND wbxl_text_id=wbx_id AND wbx_text=%s""",
                    [wbxl_language, wbx_text])
            wbxl_id = cur.fetchone()[0]
        except Exception:
            cur.execute("INSERT INTO wbt_text_in_lang VALUES(NULL,%s,%s)",
                        [wbxl_language, wbx_id])
            cur.execute("SELECT LAST_INSERT_ID()")
            wbxl_id = cur.fetchone()[0]
        return wbxl_id

    def get_wbx_id(self, cur=None, wbx_text=None):
        """Returns wbx_id (int) in wbt_text-table for given wbx_text (str)"""
        try:
            cur.execute("SELECT wbx_id FROM wbt_text WHERE wbx_text=%s", [wbx_text])
            wbx_id = cur.fetchone()[0]
        except Exception:
            cur.execute("INSERT INTO wbt_text VALUES(NULL,%s)", [wbx_text])
            cur.execute("SELECT LAST_INSERT_ID()")
            wbx_id = cur.fetchone()[0]
        return wbx_id

    def get_model_id(self, content_model=None):
        """Returns model_id (int) for the given content_model in content_models-table"""
        cur = self.conn.cursor()
        q = "SELECT model_id FROM content_models WHERE model_name='{db_content_model}'""".format(
            db_content_model=content_model)
        cur.execute(q)
        mid = cur.fetchone()[0]
        cur.close()
        return mid

    def update_wb_id_counters(self, new_eid=None, content_model=None):
        """Inserts the new QID into wb_id_counters-table"""
        cur = self.conn.cursor()
        q = "INSERT INTO wb_id_counters(id_value,id_type) VALUES(1,'{content_model}') ON DUPLICATE KEY UPDATE id_value = id_value + 1".format(
            content_model=content_model)
        cur.execute(q)
        cur.close()

    def search_text_str(self, substring=None, strict=None):
        """Searches a substring in old_text of text-table and returns page_title"""
        cur = self.conn.cursor()
        try:
            if strict:
                q1 = """SELECT old_id FROM text WHERE old_text LIKE '%"{substr}"%'""".format(
                    substr=substring)
            else:
                q1 = """SELECT old_id FROM text WHERE old_text LIKE '%{substr}%'""".format(
                    substr=substring)
            cur.execute(q1)
            ids = ', '.join([str(x[0]) for x in cur.fetchall()])
            q2 = "SELECT page_title FROM page WHERE page_latest in (" + ids + ")"
            cur.execute(q2)
            eids = [x[0].decode('utf-8') for x in cur.fetchall()]
        except Exception:
            eids = []
        cur.close()
        return eids

    def search_text_eid(self, eid=None):
        """Searches eid in old_text of text-table and returns old_id and old_text"""
        cur = self.conn.cursor()
        try:
            q1 = """SELECT old_id, old_text FROM text WHERE old_text LIKE '%"id":"{db_eid}"%'""".format(
                db_eid=eid)
            cur.execute(q1)
            out = cur.fetchone()
        except Exception:
            out = ()
        cur.close()
        return out

    def get_old_lendata(self, page_id=None):
        """Returns old len(data) for the given page_id."""
        cur = self.conn.cursor()
        q = """SELECT rc_new_len FROM recentchanges WHERE rc_id <= '{db_page_id}' ORDER BY rc_id DESC LIMIT 1""".format(
            db_page_id=page_id)
        cur.execute(q)
        out = cur.fetchone()[0]
        return out

    def get_page_latest(self, page_title=None, namespace=None):
        """Returns [page_id (int), page_latest (int)] in page-table for the 
        given page_title and namespace"""
        cur = self.conn.cursor()
        q = """SELECT page_id, page_latest FROM page WHERE page_title='{db_page_title}' and page_namespace='{db_page_namespace}'""".format(
            db_page_title=page_title,
            db_page_namespace=namespace)
        cur.execute(q)
        (page_id, page_latest) = cur.fetchall()[0]
        cur.close()
        return [page_id, page_latest]

    def get_ids(self, new=None, page_title=None, namespace=None):
        """Returns [text_id, page_id, comment_id, content_id, rev_id]"""
        if new:
            rev_id = self.get_rev_id() + 1
            page_id = self.get_page_id() + 1
        if not new:
            [page_id, rev_id] = self.get_page_latest(page_title=page_title, namespace=namespace)
        text_id = self.get_text_id() + 1
        comment_id = self.get_comment_id() + 1
        content_id = self.get_content_id() + 1
        return [text_id, page_id, comment_id, content_id, rev_id]

    def insert(self, text_id=None, text=None, page_id=None, page_title=None,
               comment_id=None, content_id=None, model_id=None,
               content_model=None, namespace=None,
               rev_id=None, new=False, ip=None):
        """Inserts data into 9 tables during creation and edit of a page"""
        timenow = re.sub("[^0-9]", "", datetime.datetime.utcnow().isoformat())[0:14]
        len_data = len(text)
        sha1hash = hashlib.sha1(text.encode()).hexdigest()[0:31]
        if new:
            action = 'create'
        else:
            action = 'edit'
        comment = "/* wbeditentity-" + action + "-" + content_model + ":0| */"
        chash = hash(comment) % 10 ** 9
        cur = self.conn.cursor()
        if new is True:
            page_latest = rev_id
            rev_parent_id = 0
            rc_source = "mw.new"
            rc_last_oldid = 0
            rc_type = 1
            rc_old_len = 0
        elif new is False:
            rev_parent_id = rev_id
            rc_source = "mw.edit"
            rc_last_oldid = rev_id
            rc_type = 0
            rc_old_len = self.get_old_lendata(page_id=page_id)
            rev_id = self.get_rev_id() + 1
            page_latest = rev_id
        else:
            raise ValueError('{} is not a valid "new" parameter. Use "True" or "False".'.format(new))
        cur.execute("INSERT INTO text VALUES(%s,%s,'utf-8')", [text_id, text])
        cur.execute("REPLACE INTO page VALUES(%s,%s,%s,'',0,%s,rand(),%s,%s,%s,%s,%s,NULL)",
                    [page_id, namespace, page_title, int(new), timenow, timenow, page_latest, len_data, content_model])
        cur.execute("INSERT INTO revision VALUES(NULL,%s,0,0,%s,0,0,%s,%s,%s)",
                    [page_id, timenow, len_data, rev_parent_id, sha1hash])
        cur.execute("INSERT INTO comment VALUES(%s,%s,%s,NULL)",
                    [comment_id, chash, comment])
        cur.execute("INSERT INTO revision_comment_temp VALUES (%s,%s)",
                    [rev_id, comment_id])
        cur.execute("INSERT INTO revision_actor_temp VALUES(%s,1,%s,%s)",
                    [rev_id, timenow, page_id])
        cur.execute("INSERT INTO content VALUES(%s,%s,%s,%s,%s)",
                    [content_id, len_data, sha1hash, model_id, 'tt:' + str(text_id)])
        cur.execute("INSERT INTO slots VALUES(%s,1,%s,%s)",
                    [text_id, content_id, text_id])
        cur.execute("INSERT INTO recentchanges VALUES (NULL,%s,1,%s,%s,%s,0,0,%s,%s,%s,%s,%s,%s,2,%s,%s,%s,0,0,NULL,'','')",
                    [timenow, namespace, page_title, comment_id, int(new), page_id, rev_id, rc_last_oldid, rc_type, rc_source, ip, rc_old_len, len_data])
        cur.close()

    def insert_secondary(self, fingerprint=None, new_eid=None, content_model=None):
        """Inserts fingerprint data into 5 (4 per item or property) secondary tables"""
        cur = self.conn.cursor()
        if content_model=='wikibase-item':
            for key, v in fingerprint.items():
                wby_id = self.wbt_types.get(key) # key is 'label', 'alias' or 'description'; wby_id is the corresponding id
                for lang, values in v.items():
                    values = [values] if isinstance(values, dict) else values # for labels and descriptions only, to make them consistent with aliases
                    for value in values:
                        wbx_text = self.conn.escape_string(value['value'])[:255] # escaping & truncating
                        wbx_id = self.get_wbx_id(cur=cur, wbx_text=wbx_text) # wbt_text
                        wbxl_id = self.get_wbxl_id(cur=cur, wbxl_language=lang, wbx_text=wbx_text, wbx_id=wbx_id) # wbt_text_in_lang
                        wbtl_id = self.get_wbtl_id(cur=cur, wbtl_type_id=wby_id, wbxl_language=lang, wbx_text=wbx_text, wbxl_id=wbxl_id) # wbt_term_in_lang
                        cur.execute("INSERT IGNORE INTO wbt_item_terms VALUES(NULL,%s,%s)", [new_eid, wbtl_id])
        if content_model=='wikibase-property':
            for key, v in fingerprint.items():
                wby_id = self.wbt_types.get(key) # key is 'label', 'alias' or 'description'; wby_id is the corresponding id
                for lang, values in v.items():
                    values = [values] if isinstance(values, dict) else values # for labels and descriptions only, to make them consistent with aliases
                    for value in values:
                        wbx_text = self.conn.escape_string(value['value'])[:255] # escaping & truncating
                        wbx_id = self.get_wbx_id(cur=cur, wbx_text=wbx_text) # wbt_text
                        wbxl_id = self.get_wbxl_id(cur=cur, wbxl_language=lang, wbx_text=wbx_text, wbx_id=wbx_id) # wbt_text_in_lang
                        wbtl_id = self.get_wbtl_id(cur=cur, wbtl_type_id=wby_id, wbxl_language=lang, wbx_text=wbx_text, wbxl_id=wbxl_id) # wbt_term_in_lang
                        cur.execute("INSERT IGNORE INTO wbt_property_terms VALUES(NULL,%s,%s)", [new_eid, wbtl_id])
        cur.close()
