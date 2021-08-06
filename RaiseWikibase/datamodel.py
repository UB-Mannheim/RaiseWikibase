import uuid


def label(language='en', value=''):
    """Create and return the JSON representation of a label (dict)

    :param language: language code used for the label, default is 'en'
    :type language: str
    :param value: a label in the specified language
    :type value: str
    :return: a dictionary with a label in the specified language
    :rtype: dict
    """
    return {language: {'language': language, 'value': value}}


def alias(language='en', value=''):
    """Create and return the JSON representation of an alias (dict)

    :param language: language code used for the alias, default is 'en'
    :type language: str
    :param value: an alias or aliases in the specified language
    :type value: str or list of str
    :return a: a dictionary with aliases in the specified language
    :rtype a: dict
    """
    a = {}
    if len(value) == 0:
        a[language] = [{'language': language, 'value': ''}]
    else:
        a[language] = [{'language': language, 'value': val} for val in value]
    return a


def description(language='en', value=''):
    """Create and return the JSON representation of a description (dict)

    :param language: language code used for the description, default is 'en'
    :type language: str
    :param value: a description in the specified language
    :type value: str
    :return: a dictionary with a description in the specified language
    :rtype: dict
    """
    return {language: {'language': language, 'value': value}}


def snak(datatype='', value='', prop='', snaktype='value'):
    """Create and return the JSON representation of a snak (dict)

    :param datatype: a one of 18 datatypes in the Wikibase data model
    :type datatype: str
    :param value: datavalue
    :type value: str for datatype in ['', 'string', 'math', 'external-id', 
                                      'url', 'commonsMedia', 'localMedia',
                                      'geo-shape', 'musical-notation', 'tabular-data',
                                      'wikibase-item', 'wikibase-property',
                                      'wikibase-lexeme', 'wikibase-form',
                                      'wikibase-sense']
                list for datatype in ['time', 'monolingualtext', 'quantity',
                                      'globe-coordinate']
    :param prop: A property ID for the snak
    :type prop: str
    :param snaktype: A type of this snak, i.e., one of ['value', 'novalue', 'somevalue'],
                    default is 'value'
    :type snaktype: str
    :return snak: a template dictionary with a snak
    :rtype snak: dict
    """
    if datatype in ['', 'string', 'math', 'external-id', 'url', 'commonsMedia',
                    'localMedia', 'geo-shape', 'musical-notation', 'tabular-data']:
        datavalue = {
            'value': value,
            'type': 'string'
        }
    elif datatype == 'wikibase-item':
        datavalue = {
            'value': {
                'entity-type': 'item',
                'numeric-id': value[1:],
                'id': value
            },
            'type': 'wikibase-entityid'
        }
    elif datatype == 'wikibase-property':
        datavalue = {
            'value': {
                'entity-type': 'property',
                'numeric-id': value[1:],
                'id': value
            },
            'type': 'wikibase-entityid'
        }
    elif datatype == 'time':
        time, timezone, precision, calendarmodel = value
        datavalue = {
            'value': {
                'time': time,
                'timezone': timezone,
                'before': 0,
                'after': 0,
                'precision': precision,
                'calendarmodel': calendarmodel  # http://www.wikidata.org/entity/Q1985727
            },
            'type': 'time'
        }
    elif datatype == 'monolingualtext':
        val, language = value
        datavalue = {
            'value': {
                'text': val,
                'language': language
            },
            'type': 'monolingualtext'
        }
    elif datatype == 'quantity':
        val, unit, upper_bound, lower_bound = value
        datavalue = {
            'value': {
                'amount': val,
                'unit': unit,
                'upperBound': upper_bound,
                'lowerBound': lower_bound
            },
            'type': 'quantity'
        }
    elif datatype == 'globe-coordinate':
        latitude, longitude, precision, globe = value
        datavalue = {
            'value': {
                'latitude': latitude,
                'longitude': longitude,
                'precision': precision,
                'globe': globe
            },
            'type': 'globecoordinate'
        }
    elif datatype == 'wikibase-lexeme':
        datavalue = {
            'value': {
                'entity-type': 'lexeme',
                'numeric-id': value[1:],
                'id': value
            },
            'type': 'wikibase-entityid'
        }
    elif datatype == 'wikibase-form':
        datavalue = {
            'value': {
                'entity-type': 'form',
                'id': value
            },
            'type': 'wikibase-entityid'
        }
    elif datatype == 'wikibase-sense':
        datavalue = {
            'value': {
                'entity-type': 'sense',
                'id': value
            },
            'type': 'wikibase-entityid'
        }
    else:
        raise ValueError('{} is not a valid datatype'.format(datatype))
    if snaktype in ['value', 'novalue', 'somevalue']:
        snak = {'snaktype': snaktype,
                'property': prop,
                'datavalue': datavalue,
                'datatype': datatype}
    else:
        raise ValueError("""{} is not a valid snaktype. Use "value, "novalue" or "somevalue".""".format(snaktype))
    return snak


def claim(prop='', mainsnak=snak(), qualifiers=[], references=[]):
    """Create and return the JSON representation of a claim (dict)

    :param prop: The property identifier for this claim
    :type prop: str
    :param mainsnak: the main snak for this claim
    :type mainsnak: dict
    :param qualifiers: a list of qualifiers
    :type qualifiers: list
    :param references: a list of references
    :type references: list
    :return: a dictionary with a claim
    :rtype: dict
    """
    return {prop: [{'mainsnak': {**mainsnak, **{'hash': str(uuid.uuid4())}},
                    'type': 'statement',
                    'rank': 'normal',
                    'qualifiers': {prop: qualifiers},
                    'qualifiers-order': [prop],
                    'references': [{'snaks': {prop: references}, 'snaks-order': [prop]}],
                    'id': ''}]}


def mainsnak(prop='', snak=snak(), qualifiers=[], references=[]):
    """Create and return the JSON representation of a mainsnak (dict) with qualifiers & references

    :param prop: The property identifier for this mainsnak
    :type prop: str
    :param snak: the snak for this mainsnak
    :type snak: dict
    :param qualifiers: a list of qualifiers
    :type qualifiers: list
    :param references: a list of references
    :type references: list
    :return: a dictionary with a mainsnak, qualifiers & references
    :rtype: dict
    """
    return {'mainsnak': {**snak, **{'hash': str(uuid.uuid4())}},
            'type': 'statement',
            'rank': 'normal',
            'qualifiers': {prop: qualifiers},
            'qualifiers-order': [prop],
            'references': [{'snaks': {prop: references}, 'snaks-order': [prop]}],
            'id': ''}


def statement(prop='', mainsnaks=[mainsnak()]):
    """Create and return the JSON representation of a statement (dict)

    :param prop: The property identifier for this statement
    :type prop: str
    :param mainsnaks: a list of mainsnaks for this statement
    :type mainsnak: list
    :return: a dictionary with a statement
    :rtype: dict
    """
    return {prop: mainsnaks}


def entity(labels={}, aliases={}, descriptions={}, claims={}, etype='', datatype=''):
    """Create and return the JSON representation of an entity (dict)

    :param labels: A dictionary with labels. Default is empty dict.
    :type labels: dict
    :param aliases: A dictionary with aiases. Default is empty dict.
    :type aliases: dict
    :param descriptions: A dictionary with descriptions. Default is empty dict.
    :type descriptions: dict
    :param claims: A dictionary with claims. Default is empty dict.
    :type claims: dict
    :param etype: Entity type. For example, 'item' or 'property'.
    :type etype: str
    :param datatype: A datatype of an entity. This applies only to 'etype'=='property'.
    :type datatype: str
    :return entity: a dictionary with JSON representation of an entity
    :rtype entity: dict
    """
    entity = {'type': etype,
              'datatype': datatype,
              'id': '',
              'labels': labels,
              'aliases': aliases,
              'descriptions': descriptions,
              'claims': claims}
    if etype == 'item':
        entity.pop('datatype')
    return entity


"https://www.mediawiki.org/wiki/Extension_default_namespaces"
namespaces = {'wikibase-item': 120,
              'wikibase-property': 122,
              'main': 0,
              'media': -2,
              'special': -1,
              'talk': 1,
              'user': 2,
              'user_talk': 3,
              'project': 4,
              'project_talk': 5,
              'file': 6,
              'file_talk': 7,
              'mediawiki': 8,
              'mediawiki_talk': 9,
              'template': 10,
              'template_talk': 11,
              'help': 12,
              'help_talk': 13,
              'category': 14,
              'category_talk': 15,
              'Scribunto': 828}

"https://github.com/SuLab/WikidataIntegrator/blob/main/notebooks/CreateWikidataProperties.ipynb"
datatypes = {'http://wikiba.se/ontology#CommonsMedia': 'commonsMedia',
             'http://wikiba.se/ontology#ExternalId': 'external-id',
             'http://wikiba.se/ontology#GeoShape': 'geo-shape',
             'http://wikiba.se/ontology#GlobeCoordinate': 'globe-coordinate',
             'http://wikiba.se/ontology#Math': 'math',
             'http://wikiba.se/ontology#Monolingualtext': 'monolingualtext',
             'http://wikiba.se/ontology#Quantity': 'quantity',
             'http://wikiba.se/ontology#String': 'string',
             'http://wikiba.se/ontology#TabularData': 'tabular-data',
             'http://wikiba.se/ontology#Time': 'time',
             'http://wikiba.se/ontology#Url': 'url',
             'http://wikiba.se/ontology#WikibaseItem': 'wikibase-item',
             'http://wikiba.se/ontology#WikibaseLexeme': 'lexeme',
             'http://wikiba.se/ontology#WikibaseForm': 'form',
             'http://wikiba.se/ontology#WikibaseSense': 'sense',
             'http://wikiba.se/ontology#MusicalNotation': 'musical-notation',
             'http://wikiba.se/ontology#WikibaseProperty': 'wikibase-property'}
