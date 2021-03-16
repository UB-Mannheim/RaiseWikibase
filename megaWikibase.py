from RaiseWikibase.dbconnection import DBConnection
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity, namespaces, datatypes
from RaiseWikibase.utils import get_wikidata_properties
from RaiseWikibase.raiser import page, batch, building_indexing
from pathlib import Path
import requests
import time
import numpy as np
import csv


def property_wid(prop=''):
    """Create a simplified JSON represetation (only the label, aliases, 
    description and one claim) of the first local property 'Wikidata ID'"""
    p = entity(labels=label(value='Wikidata ID'),
               aliases=alias(value=["WID", 'WikidataID']),
               descriptions=description(value="ID of an entity in Wikidata"),
               claims=claim(prop='P2',
                            mainsnak=snak(datatype='string',
                                          value='http://www.wikidata.org/entity/$1',
                                          prop='P2',
                                          snaktype='value')),
               etype='property',
               datatype='external-id')
    p['claims'].update(claim(prop='P3',
                             mainsnak=snak(datatype='string',
                                           value='http://www.wikidata.org/entity/$1',
                                           prop='P3',
                                           snaktype='value')))
    return p


def property_wd(prop=''):
    """For the given PID of a property in Wikidata returns its 
    simplified JSON represetation (only the label, aliases, description 
    and one claim)"""
    if prop:
        r = requests.get('https://www.wikidata.org/entity/' + prop + '.json').json()
        po = r.get('entities').get(prop)
        p = entity(labels=po.get('labels'),
                   aliases=po.get('aliases'),
                   descriptions=po.get('descriptions'),
                   claims=claim(prop='P1',
                                mainsnak=snak(datatype='external-id',
                                              value=prop,
                                              prop='P1',
                                              snaktype='value')),
                   etype='property',
                   datatype='string')
    else:
        p = None
    return p


def property_hrn(prop=''):
    """Create a simplified JSON represetation (only the label, aliases, 
    description and one claim) of the first local property 'Native company number'"""
    p = entity(labels=label(value='Native company number'),
               aliases=alias(value=["Court, code and number", 'Register, type of register and company number',
                                    'Registergericht, Registerart and Handelsregister number ']),
               descriptions=description(
                   value="The registration authority (Amtsgericht), the registration code and the registration number"),
               claims={},
               etype='property',
               datatype='external-id')
    return p


def property_wd_all():
    """ Send a SPARQL-request to Wikidata, get all properties with labels,
    aliases, descriptions and datatypes, and return a list of JSON 
    representations of the properties"""
    props = get_wikidata_properties(language='en')
    props = props.replace(np.nan, '').replace("http://www.wikidata.org/entity/", "", regex=True)
    props = props.groupby(['propertyWikidata', 'propertyType',
                           'propertyLabel', 'propertyDescription']
                          ).agg(propertyAlias=('propertyAlias', lambda x: list(x)),
                                fURL=('fURL', lambda x: list(x)),
                                cURI=('cURI', lambda x: list(x)),
                                ).reset_index()
    props = props[props.propertyWikidata != ("P1630" or "P1921")]
    props = props.sort_values(by=['propertyWikidata'],
                              key=lambda col: col.str.replace('P', '', regex=True).astype(float))
    plist = []
    for ind, row in props.iterrows():
        url, dtype, title, desc, alia, furl, curi = row
        p = entity(labels=label(value=title),
                   aliases=alias(value=alia),
                   descriptions=description(value=desc),
                   claims=claim(prop='P1',
                                mainsnak=snak(datatype='external-id',
                                              value=url,
                                              prop='P1',
                                              snaktype='value')),
                   etype='property',
                   datatype=datatypes[dtype])
        for f in furl:
            if f != '':
                p['claims'].update(claim(prop='P2',
                                         mainsnak=snak(datatype='string',
                                                       value=f,
                                                       prop='P2',
                                                       snaktype='value')))
        for c in curi:
            if c != '':
                p['claims'].update(claim(prop='P3',
                                         mainsnak=snak(datatype='string',
                                                       value=c,
                                                       prop='P3',
                                                       snaktype='value')))
        plist.append(p)
    return plist


def fill_texts():
    """Fill all texts from the texts-folder"""
    connection = DBConnection()
    cmodelpath = "./texts/"
    cmodels = ['wikitext', 'Scribunto']
    for cmodel in cmodels:
        p = Path(cmodelpath + cmodel)
        folders = [x for x in p.iterdir() if x.is_dir()]
        for folder in folders:
            ns = namespaces[folder.name]
            files = [x for x in folder.iterdir() if x.is_file()]
            for file in files:
                pt = file.name.replace(':', '/')
                if pt.endswith('.css'):
                    cm = 'sanitized-css'
                else:
                    cm = cmodel
                text = file.read_text("utf-8")
                print(ns, pt, cmodel)
                page(connection, cm, ns, text, pt, True)
    # Fill the Main page separately
    pt = "Main_Page"
    p = Path(cmodelpath + pt)
    text = p.read_text("utf-8")
    page(connection, 'wikitext', 0, text, pt, False)
    connection.conn.commit()
    connection.conn.close()


if __name__ == "__main__":

    time0 = time.time()

    # Create first four properties in a local Wikibase
    p1 = property_wid()
    p2 = property_wd('P1630')
    p3 = property_wd('P1921')
    p4 = property_hrn()
    batch('wikibase-property', [p1, p2, p3, p4])

    # Create 8400+ Wikidata properties except of the already created p2 and p3.
    plist = property_wd_all()
    batch('wikibase-property', plist)

    # Fill all texts
    fill_texts()

    connection = DBConnection()
    [opencorporatesid] = connection.search_text_str('OpenCorporates ID', strict=True)
    [streetaddress] = connection.search_text_str('street address', strict=True)
    [retrieved] = connection.search_text_str('retrieved', strict=True)
    [handelnumber] = connection.search_text_str('Native company number', strict=True)
    connection.conn.close()

    # Process OpenCorporates dataset
    # Download https://daten.offeneregister.de/openregister.db.gz
    # Unzip and run in shell:
    # sqlite3 -header -csv handelsregister.db "select * from company;" > millions_companies.csv
    time1 = time.time()
    items = []
    path_to_ofreg = "./millions_companies.csv"
    p = Path(path_to_ofreg)
    if p.is_file():
        with p.open('r') as f:
            reader = csv.reader(f, delimiter=",")
            for i, line in enumerate(reader):
                if i > 0:
                    [orid, company_number, current_status, jurisdiction_code, name,
                     registered_address, retrieved_at, register_flag_AD, register_flag_CD,
                     register_flag_DK, register_flag_HD, register_flag_SI, register_flag_UT,
                     register_flag_VOE, federal_state, native_company_number, registered_office,
                     registrar, register_art, register_nummer, former_registrar, register_flag_,
                     register_flag_Note, registerNummerSuffix, register_flag_Status_information] = line
                    e = entity(labels=label(value=name),
                               aliases={},
                               descriptions={},
                               claims=claim(prop=opencorporatesid,
                                            mainsnak=snak(datatype='external-id',
                                                          value='de/' + company_number,
                                                          prop=opencorporatesid,
                                                          snaktype='value'),
                                            qualifiers=[snak("time", ['+' + retrieved_at, 0, 11,
                                                                      'http://www.wikidata.org/entity/Q1985727'],
                                                             retrieved, 'value')],
                                            references=[snak('external-id', 'de/' + company_number,
                                                             opencorporatesid, 'value')]),
                               etype='item')
                    if registered_address:
                        e['claims'].update(claim(prop=streetaddress,
                                                 mainsnak=snak(datatype='monolingualtext',
                                                               value=[registered_address, 'en'],
                                                               prop=streetaddress,
                                                               snaktype='value'),
                                                 qualifiers=[snak("time", ['+' + retrieved_at, 0, 11,
                                                                           'http://www.wikidata.org/entity/Q1985727'],
                                                                  retrieved, 'value')],
                                                 references=[snak('external-id', 'de/' + company_number,
                                                                  opencorporatesid, 'value')]))
                    if native_company_number:
                        e['claims'].update(claim(prop=handelnumber,
                                                 mainsnak=snak(datatype='external-id',
                                                               value=native_company_number,
                                                               prop=handelnumber,
                                                               snaktype='value'),
                                                 qualifiers=[snak("time", ['+' + retrieved_at, 0, 11,
                                                                           'http://www.wikidata.org/entity/Q1985727'],
                                                                  retrieved, 'value')],
                                                 references=[snak('external-id', 'de/' + company_number,
                                                                  opencorporatesid, 'value')]))
                    items.append(e)
                    del e
                if i % 100000 == 0:
                    batch('wikibase-item', items)
                    print(time.time() - time1)
                    items = []

    # to make the KG production-ready, execute the following as well
    # or run in shell 'docker-compose down' and 'docker-compose up -d' again
    # building_indexing() 

    print(time.time() - time0)
