# RaiseWikibase

* Fast inserts into a Wikibase instance.
* Creates up to a million entities and wikitexts per hour.
* Includes a reusable example of the BERD knowledge graph construction.

## Table of contents
- [How to use](#how-to-use)
- [Performance experiments](#performance)
- [A reusable example of the BERD knowledge graph construction](#example)

## How to use

Clone or download the RaiseWikibase directory.

### Wikibase Docker

Copy `env.tmpl` to `.env` and substitute the default values with your
own usernames and passwords. Run `docker-compose up -d` in the main RaiseWikibase folder. 
Check whether it's running using `docker-compose logs -f`.

### Functionality

First, check the [Wikibase Data Model](https://www.mediawiki.org/wiki/Wikibase/DataModel) and try RaiseWikibase functions for it:
```python
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity, namespaces, datatypes
```

To create the JSON representation of an item with with the English label `Wikibase`, try:
```python
itemjson = entity(labels=label(value='Wikibase'), etype='item')
```

To create one thousand of items with that JSON representation, try:
```python
from RaiseWikibase.raiser import batch
batch(content_model='wikibase-item', texts=[itemjson for i in range(1000)])
```

## Performance experiments

The script runs two performance experiments for creating the wikitexts and items. Run it in shell:
```shell
python3 RaisingWikibase.py
```
It saves the CSV files with results and creates the pdf files with figures in `./experiments/`.

## A reusable example of the BERD knowledge graph construction

The script creates a knowledge graph from scratch. Before running it prepare the OpenCorporates dataset.
Download https://daten.offeneregister.de/openregister.db.gz. Unzip it and run in shell:
```shell
sqlite3 -header -csv handelsregister.db "select * from company;" > millions_companies.csv
```
Put `millions_companies.csv` to the main RaiseWikibase folder.

Run:
```shell
python3 RaisingBERD.py
```









