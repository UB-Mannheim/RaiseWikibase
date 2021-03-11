# RaiseWikibase

* Fast inserts into a Wikibase instance.
* Creates up to a million entities and wikitexts per hour.
* Creates a mini Wikibase instance with Wikidata properties in a few minutes.
* Creates the BERD knowledge graph with millions of entities in a few hours.

## Table of contents
- [How to use](#how-to-use)
- [Performance analysis](#performance-analysis)
- [Creating a mini Wikibase instance in a few minutes](#creating-a-mini-wikibase-instance-in-a-few-minutes)
- [Creating the BERD instance with millions of entities in a few hours](#creating-the-berd-instance-with-millions-of-entities-in-a-few-hours)
- [Deployment in production](#deployment-in-production)
- [Acknowledgments](#acknowledgments)

## How to use

Clone the RaiseWikibase repository: 
```shell
git clone https://github.com/UB-Mannheim/RaiseWikibase
```

Install RaiseWikibase via `pip3`:
```shell
cd RaiseWikibase/
pip3 install -e .
```

The versions of the RaiseWikibase related libraries can be found in `setup.py`.

### Wikibase Docker

RaiseWikibase is solely based on [Wikibase Docker](https://github.com/wmde/wikibase-docker) developed by [Wikimedia Germany](https://wikimedia.de). It significantly simplifies deployment of a Wikibase instance. The versions of the Wikibase related software can be found in `docker-compose.yml`: `wikibase:1.35-bundle`, `mariadb:10.3`, `wdqs:0.3.40` and `elasticsearch:6.5.4-extra`. The image `wdqs:0.3.40` is a Wikibase specific [Blazegraph](https://blazegraph.com) image.

Copy `env.tmpl` to `.env` and substitute the default values with your
own usernames and passwords.

Run in the main RaiseWikibase folder:
```shell
docker-compose up -d
```

If it runs first time, it pulls the Wikibase Docker images. Then it builds, creates, starts, and attaches to containers for a service.
Check whether it's running using:
```shell
docker ps
```

If it's running, the output is like this:
```shell
CONTAINER ID        IMAGE                                COMMAND                   CREATED              STATUS              PORTS                       NAMES
0cac985f00a5        wikibase/quickstatements:latest      "/bin/bash /entrypoi..."    About a minute ago   Up About a minute   0.0.0.0:9191->80/tcp        raisewikibase_quickstatements_1
2f277b599ea0        wikibase/wdqs:0.3.40                 "/entrypoint.sh /run..."    About a minute ago   Up About a minute                               raisewikibase_wdqs-updater_1
3d7e6462b290        wikibase/wdqs-frontend:latest        "/entrypoint.sh ngin..."    About a minute ago   Up About a minute   0.0.0.0:8282->80/tcp        raisewikibase_wdqs-frontend_1
ef945d05fc88        wikibase/wikibase:1.35-bundle        "/bin/bash /entrypoi..."    About a minute ago   Up About a minute   0.0.0.0:8181->80/tcp        raisewikibase_wikibase_1
10df54332657        wikibase/wdqs-proxy                  "/bin/sh -c \"/entryp..."   About a minute ago   Up About a minute   0.0.0.0:8989->80/tcp        raisewikibase_wdqs-proxy_1
37f34328b73f        wikibase/wdqs:0.3.40                 "/entrypoint.sh /run..."    About a minute ago   Up About a minute   9999/tcp                    raisewikibase_wdqs_1
9a1c8ddd8c89        wikibase/elasticsearch:6.5.4-extra   "/usr/local/bin/dock..."    About a minute ago   Up About a minute   9200/tcp, 9300/tcp          raisewikibase_elasticsearch_1
b640eaa556e3        mariadb:10.3                         "docker-entrypoint.s..."    About a minute ago   Up About a minute   127.0.0.1:63306->3306/tcp   raisewikibase_mysql_1
```

The logs can viewed via:
```shell
docker-compose logs -f
```

Usually in less than a minute from the start you will see the messages from `wdqs-updater_1` in the logs: `INFO  o.w.q.r.t.change.RecentChangesPoller - Got no real changes` and `INFO  org.wikidata.query.rdf.tool.Updater - Sleeping for 10 secs`. The Wikibase front-end (http://localhost:8181) and query service (http://localhost:8282) are already available. Data filling can be started.

If you want to stop the Wikibase Docker, to remove all your uploaded data and to run a fresh Wikibase instance, use:
```shell
docker-compose down
sudo rm -rf mediawiki-*  query-service-data/ quickstatements-data/
docker-compose up -d
```

### Wikibase Data Model and RaiseWikibase functions for it

The [Wikibase Data Model](https://www.mediawiki.org/wiki/Wikibase/DataModel) is an ontology describing the structure of the data in Wikibase. A non-technical summary of the Wikibase model is available at [DataModel/Primer](https://www.mediawiki.org/wiki/Wikibase/DataModel/Primer). The initial [conceptual specification](https://www.mediawiki.org/wiki/Wikibase/DataModel)
for the Data Model was created by [Markus Krötzsch](http://korrekt.org/)
and [Denny Vrandečić](http://simia.net/wiki/Denny), with minor contributions by
Daniel Kinzler and Jeroen De Dauw. The Wikibase Data Model has been implemented by [Jeroen De Dauw](https://www.EntropyWins.wtf)
and Thiemo Kreuz as [Wikimedia Germany](https://wikimedia.de) employees for the [Wikidata project](https://wikidata.org/).

RaiseWikibase provides the functions for the Wikibase Data Model:
```python
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity
```

The functions `entity()`, `claim()`, `snak()`, `description()`, `alias()`and `label()` return the template dictionaries. So all basic operations with dictionaries in Python can be used. You can merge two dictionaries `X` and `Y` using `X | Y` (since Python 3.9) and using `{**X, **Y}` (since Python 3.5).

Let's check the Wikidata entity [Q43229](https://www.wikidata.org/wiki/Q43229). You can create both English and German labels for the entity using RaiseWikibase:
```python
labels = {**label('en', 'organization'), **label('de', 'Organisation')}
```

Multiple English and German aliases can also be easily created:
```python
aliases = {**alias('en', ['organisation', 'org']), **alias('de', ['Org', 'Orga'])}
```

Multilingual descriptions can be added:
```python
descriptions = {**description('en', 'social entity (not necessarily commercial)'),
		**description('de', 'soziale Struktur mit einem gemeinsamen Ziel')}
```

To add statements (claims), qualifiers and references, we need a `snak()` function. To create a snak, we have to specify `property`, `datavalue`, `datatype` and `snaktype`. For example, if our Wikibase instance has the property with ID `P1`, a label `Wikidata ID` and datatype `external-id`, we can create a mainsnak with that property and the value 'Q43229':
```python
mainsnak = snak(datatype='external-id', value='Q43229', prop='P1', snaktype='value')
```

Just as an example of creating the qualifiers and references, let's add:
```python
qualifiers = [snak(datatype='external-id', value='Q43229', prop='P1', snaktype='value')]
references = [snak(datatype='external-id', value='Q43229', prop='P1', snaktype='value')]
```

We have now a mainsnak, qualifiers and references. Let's create a claim for an item:
```python
claims = claim(prop='P1', mainsnak=mainsnak, qualifiers=qualifiers, references=references)
```

All ingredients for creating the JSON representation of an item are ready. The `entity()` function does the job:
```python
item = entity(labels=labels, aliases=aliases, descriptions=descriptions, claims=claims, etype='item')
```

If the property needs to be created, the datatype has to be additionally specified:
```python
property = entity(labels=labels, aliases=aliases, descriptions=descriptions,
		  claims=claims, etype='property', datatype='string')
```

Note that these functions create only the dictionaries for the corresponding elements of the Wikibase Data Model. Writing into the database happens using the `page` and `batch` functions.

### Creating pages (entities and texts) in Wikibase

To create one thousand items with the already created JSON representation of an item, use:
```python
from RaiseWikibase.raiser import batch
batch(content_model='wikibase-item', texts=[item for i in range(1000)])
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

The script `performance.py` runs two performance experiments for creating the wikitexts and items. Run it in shell:
```shell
python3 performance.py
```

The variable `batch_lengths` is set to `[100]`. This means the length of a batch in each experiment is `100`. Running both experiments in this case takes 80 seconds. You can set it to `[100, 200, 300]` in order to run experiments for different batch lengths. To reproduce Figures 1a and 1b, set `batch_lengths` to `[10000]`.

The script saves the CSV files with numeric values of results and creates the pdf files with figures in `./experiments/`.

| (1a) Wikitexts | (1b) Items |
|:------:|:------:|
| ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/exp1.png) | ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/exp2.png) |

The insert rate in pages per second is shown at Figure 1a for wikitexts and at Figure 1b for items. Every data point correspond to a batch of ten thousands pages. At Figure 1a six different data points correspond to six repeated experiments. At Figure 1b two colors correspond to two repeated experiments and three shapes of a data point correspond to three cases: 1) circle - each claim without a qualifier and without a reference, 2) x - each claim with one qualifier and without a reference, and 3) square - each claim with one qualifier and one reference.

## Creating a mini Wikibase instance in a few minutes

The script `miniWikibase.py` fills a fresh Wikibase instance with some structured and unstructured data in roughly 30 seconds. The data include 8400+ properties from Wikidata, two templates, a page with SPARQL examples, a page with a sidebar and modules. Check the folder `texts` containing unstructured data and add there your own data. Information about the Wikidata properties is queried through the Wikidata endpoint and it takes a few seconds. Run:
```shell
python3 miniWikibase.py
```

| (2a) Main page | (2b) Properties |
|:------:|:------:|
| ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/mini1.png) | ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/mini2.png) |

Figure 2a shows the main page and Figure 2b shows a list of properties. If you run the script `miniWikibase.py` with the commented line 156, you will see only the property identifiers instead of the labels. You can either uncomment line 156 or run in shell `docker-compose down` and `docker-compose up -d`.

## Creating the BERD instance with millions of entities in a few hours

The script `RaisingBERD.py` creates a knowledge graph from scratch. Before running it prepare the OpenCorporates dataset.
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
