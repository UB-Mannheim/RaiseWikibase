# RaiseWikibase

* Fast inserts into a Wikibase instance.
* Creates up to a million entities and wikitexts per hour.
* Includes a reusable example of the BERD knowledge graph construction.

## Table of contents
- [How to use](#how-to-use)
- [Performance analysis](#performance-analysis)
- [A reusable example of the BERD knowledge graph construction](#a-reusable-example-of-the-berd-knowledge-graph-construction)
- [Deployment in production](#deployment-in-production)

## How to use

Clone or download the RaiseWikibase directory.

### Wikibase Docker

Copy `env.tmpl` to `.env` and substitute the default values with your
own usernames and passwords. Run `docker-compose up -d` in the main RaiseWikibase folder. 
Check whether it's running using `docker-compose logs -f`.

### Functionality

First, check the [Wikibase Data Model](https://www.mediawiki.org/wiki/Wikibase/DataModel) and import the RaiseWikibase functions for it:
```python
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity
```

The functions `entity()`, `claim()`, `snak()`, `description()`, `alias()`and `label()` return the template dictionaries. So all basic operations with dictionaries can be used.

To create the JSON representation of an item with the English label 'Wikibase', try:
```python
itemjson = entity(labels=label(value='Wikibase'), etype='item')
```

To create one thousand items with that JSON representation, use:
```python
from RaiseWikibase.raiser import batch
batch(content_model='wikibase-item', texts=[itemjson for i in range(1000)])
```

Let `wtext` is a Python string representing a wikitext. Then, `wikitexts = [wtext for i in range(1000)]` is a list of wikitexts and `page_titles` is a list of the corresponding page titles. To create one thousand wikitexts in the main namespace, use:

```python
batch(content_model='wikitext', texts=wikitexts, namespace=0, page_title=page_titles)
```

The dictionary of namespaces can be found here:
```python
from RaiseWikibase.datamodel import namespaces
```

For example, the code for the main namespace `namespaces['main']` is `0`.

## Performance analysis

The script runs two performance experiments for creating the wikitexts and items. Run it in shell:
```shell
python3 performance.py
```
It saves the CSV files with results and creates the pdf files with figures in `./experiments/`.

| (1a) Wikitexts | (1b) Items |
|:------:|:------:|
| ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/exp1.png) | ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/exp2.png) |

The insert rate in pages per second is shown at Figure 1a for wikitexts and at Figure 1b for items. Every data point correspond to a batch of ten thousands pages. At Figure 1a six different data points correspond to six repeated experiments. At Figure 1b two colors correspond to two repeated experiments and three shapes of a data point correspond to three cases: 1) circle - each claim without a qualifier and without a reference, 2) x - each claim with one qualifier and without a reference, and 3) square - each claim with one qualifier and one reference.

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

## Deployment in production

The setting above runs on localhost.

A [setup](https://stackoverflow.com/a/63397827) for deployment using Nginx is provided by Louis Poncet ([personaldata.io](https://wiki.personaldata.io)).