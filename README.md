# RaiseWikibase

* Fast inserts into a Wikibase instance.
* Creates up to a million entities and wikitexts per hour.
* Creates a mini Wikibase instance with Wikidata properties in a few minutes.
* Includes a reusable example of the BERD knowledge graph construction.

## Table of contents
- [How to use](#how-to-use)
- [Performance analysis](#performance-analysis)
- [Creating a mini Wikibase instance in a few minutes](#creating-a-mini-wikibase-instance-in-a-few-minutes)
- [A reusable example of the BERD knowledge graph construction](#a-reusable-example-of-the-berd-knowledge-graph-construction)
- [Deployment in production](#deployment-in-production)
- [Acknowledgments](#acknowledgments)

## How to use

Clone or download the RaiseWikibase directory.

### Wikibase Docker

Copy `env.tmpl` to `.env` and substitute the default values with your
own usernames and passwords. Run `docker-compose up -d` in the main RaiseWikibase folder. 
If you run it first time, it pulls the Wikibase Docker images. Then it builds, creates, starts, and attaches to containers for a service.
Check whether it's running using `docker ps`. The logs can viewed via `docker-compose logs -f`. As soon as you see the output (without errors) from `wdqs-updater_1` in the logs, the Wikibase front-end and query service are available and data filling can be started.

If you want to stop the Wikibase Docker, to remove all your uploaded data and to run a fresh Wikibase instance, use:
```shell
docker-compose down
sudo rm -rf mediawiki-*  query-service-data/ quickstatements-data/
docker-compose up -d
```

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

The variable `batch_lengths` is set to `[100]`. This means the length of a batch in each experiment is `100`. Running both experiments in this case takes 80 seconds. To reproduce Figures 1a and 1b, set `batch_lengths` to `[10000]`.

The script saves the CSV files with numeric values of results and creates the pdf files with figures in `./experiments/`.

| (1a) Wikitexts | (1b) Items |
|:------:|:------:|
| ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/exp1.png) | ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/exp2.png) |

The insert rate in pages per second is shown at Figure 1a for wikitexts and at Figure 1b for items. Every data point correspond to a batch of ten thousands pages. At Figure 1a six different data points correspond to six repeated experiments. At Figure 1b two colors correspond to two repeated experiments and three shapes of a data point correspond to three cases: 1) circle - each claim without a qualifier and without a reference, 2) x - each claim with one qualifier and without a reference, and 3) square - each claim with one qualifier and one reference.

## Creating a mini Wikibase instance in a few minutes

The script fills a fresh Wikibase instance with 8400+ properties from Wikidata in roughly 30 seconds. Additional seven seconds are needed to query the Wikidata endpoint. Run:
```shell
python3 miniWikibase.py
```

| (2a) Main page | (2b) Properties |
|:------:|:------:|
| ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/mini1.png) | ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/mini2.png) |

Figure 2a shows the main page and Figure 2b shows a list of properties. If you run the script `miniWikibase.py` with the commented line 156, you will see only the property identifiers instead of the labels. You can either uncomment line 156 or run in shell `docker-compose down` and `docker-compose up -d`.

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

## Acknowledgments

This work was funded by the Ministry of Science, Research and Arts of Baden-Württemberg through the project [Business and Economics Research Data Center Baden-Württemberg](https://www.berd-bw.de).

We thank [Jesper Zedlitz](https://github.com/jze) for his experiments explained at [the FactGrid blog](https://blog.factgrid.de/archives/2013) and for his open source code [wikibase-insert](https://github.com/jze/wikibase-insert).