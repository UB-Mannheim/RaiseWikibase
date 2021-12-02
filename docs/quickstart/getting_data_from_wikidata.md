---
layout: default
title: Getting data from Wikidata
parent: QuickStart
nav_order: 2h
---
# Getting data from Wikidata and filling it into a Wikibase instance

The [Wikidata](https://wikidata.org/) knowledge graph already has millions of items and thousands of properties. For many projects some of these entities can be reused. Let's create the multilingual items [human](https://wikidata.org/entity/Q5), [organization](https://wikidata.org/entity/Q43229) and [location](https://wikidata.org/entity/Q17334923) in a local Wikibase instance using RaiseWikibase.

The example below defines the function `get_wd_entity`. It takes a Wikidata ID as an input, sends a request to Wikidata, gets the JSON representation of an entity, removes the keys unwanted in a local Wikibase instance, creates a claim and returns the JSON representation of the entity, if an error has not occured. The function `get_wd_entity` is used to get the JSON representations for [human](https://wikidata.org/entity/Q5), [organization](https://wikidata.org/entity/Q43229) and [location](https://wikidata.org/entity/Q17334923). These JSON representations are then filled into a local Wikibase instance using the `batch` function.

```python
from RaiseWikibase.raiser import batch
from RaiseWikibase.datamodel import claim, snak
import requests

def get_wd_entity(wid=''):
    """Returns JSON representation of a Wikidata entity for the given WID"""
    # Remove the following keys to avoid a problem with a new Wikibase instance
    remove_keys = ['lastrevid', 'pageid', 'modified', 'title', 'ns']
    try:
        r = requests.get('https://www.wikidata.org/entity/' + wid + '.json')
        entity = r.json().get('entities').get(wid)
        for key in remove_keys:
            entity.pop(key)
        entity['claims'] = claim(prop='P1',
                                 mainsnak=snak(datatype='external-id',
                                               value=wid,
                                               prop='P1',
                                               snaktype='value'),
                                 qualifiers=[],
                                 references=[])
    except Exception:
        entity = None
    return entity

wids = ['Q5', 'Q43229', 'Q17334923'] # human, organization, location
items = [get_wd_entity(wid) for wid in wids]
batch('wikibase-item', items)
```

The lines, where `entity['claims']` is rewritten, can be commented. Then, the created items contain the claims with the property IDs corresponding to Wikidata. Just try it out.

If you filled the entities from Wikidata into a fresh Wikibase instance, but you cannot open a page at http://localhost:8181/entity/Q1, run in shell:
```shell
docker exec raisewikibase_wikibase_1 bash "-c" "php maintenance/update.php --quick --force"
```

We used the property with ID 'P1' in the claim. That property with a label 'Wikidata ID' can be created using the script [miniWikibase.py](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/miniWikibase.py). It creates all 9000+ Wikidata properties in two minutes.