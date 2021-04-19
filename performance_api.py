import json
import random
import string
from tqdm import tqdm
from RaiseWikibase.datamodel import label, alias, description, snak, entity
from RaiseWikibase.api import Session
import concurrent.futures

S = Session()


def create_first_property():
    etype = 'property'
    labels = label('en', 'First property')
    ijson = entity(labels=labels, etype=etype, datatype='string')
    ijson.pop('id')
    prop = json.JSONEncoder().encode(ijson)
    S.create_entity(prop, etype=etype)


def create_random_item(x):
    etype = 'item'
    labels = label('en', ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)))
    aliases = alias('en', [''.join(random.choices(string.ascii_lowercase + string.digits, k=10))])
    descriptions = description('en', ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)))
    mainsnak = snak(datatype='external-id', value='Q43229', prop='P1', snaktype='value')
    claims = {"claims": [{'mainsnak': mainsnak, 'type': 'statement', 'rank': 'normal'}]}
    ijson = entity(labels=labels, aliases=aliases, descriptions=descriptions, claims=claims, etype=etype)
    ijson.pop('id')
    item = json.JSONEncoder().encode(ijson)
    S.create_entity(item, etype=etype)


def pqdm(f, iterator, max_workers=1):
    l = len(iterator)
    with tqdm(total=l) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(f, arg): arg for arg in iterator}
            results = {}
            for future in concurrent.futures.as_completed(futures):
                arg = futures[future]
                results[arg] = future.result()
                pbar.update(1)


create_first_property()
pqdm(create_random_item, range(100), 1)

