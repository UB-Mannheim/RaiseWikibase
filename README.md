# RaiseWikibase

```
A tool for speeding up multilingual knowledge graph construction with Wikibase
```
[[Camera-ready PDF preprint "RaiseWikibase: Fast inserts into the BERD instance" for ESWC 2021 P&D](https://openreview.net/pdf?id=87hp7LJDJE)]
* Fast inserts into a Wikibase instance: creates up to a million entities and wikitexts per hour.
* Creates a mini Wikibase instance with Wikidata properties in a few minutes.
* Creates the [BERD](https://www.berd-bw.de) knowledge graph with millions of entities in a few hours.

:warning: &nbsp; This tool is experimental. The current desire is to move its functionality to the Wikibase API, see the ticket [T287164 "Improve bulk import via API"](https://phabricator.wikimedia.org/T287164). If you are interested in improving bulk import into Wikibase, please contribute to that ticket.

## Table of contents
- [How to use](#how-to-use)
  * [Installation](#installation)
  * [Wikibase Docker](#wikibase-docker)
  * [Wikibase Extensions](#wikibase-extensions)
  * [Wikibase Data Model and RaiseWikibase functions](#wikibase-data-model-and-raisewikibase-functions)
  * [Creating entities and texts](#creating-entities-and-texts)
  * [Testing all datatypes](#testing-all-datatypes)
  * [Compatibility with WikidataIntegrator and WikibaseIntegrator](#compatibility-with-wikidataintegrator-and-wikibaseintegrator)
  * [Getting data from Wikidata and filling it into a Wikibase instance](#getting-data-from-wikidata-and-filling-it-into-a-wikibase-instance)
- [Performance analysis](#performance-analysis)
- [Creating a mini Wikibase instance with thousands of entities in a few minutes](#creating-a-mini-wikibase-instance-with-thousands-of-entities-in-a-few-minutes)
- [Creating a mega Wikibase instance with millions of BERD entities in a few hours](#creating-a-mega-wikibase-instance-with-millions-of-berd-entities-in-a-few-hours)
- [Deployment in production](#deployment-in-production)
- [Paper](#paper)
- [Acknowledgments](#acknowledgments)
- [See also](#see-also)

## How to use

### Installation

Clone RaiseWikibase and install it via `pip3`:
```shell
git clone https://github.com/UB-Mannheim/RaiseWikibase
cd RaiseWikibase/
pip3 install .
```

### Wikibase Docker

:eyes: &nbsp; [Wikibase Docker](https://github.com/wmde/wikibase-release-pipeline) is distributed under [BSD 3-Clause License](https://github.com/wmde/wikibase-release-pipeline/blob/master/LICENSE). Please fulfill the requirements.

RaiseWikibase is solely based on [Wikibase Docker](https://github.com/wmde/wikibase-release-pipeline) developed by [Wikimedia Germany](https://wikimedia.de). [Wikibase Docker](https://github.com/wmde/wikibase-release-pipeline) significantly simplifies deployment of a [Wikibase](https://github.com/wikimedia/Wikibase) instance.

:warning: &nbsp; Copy [env.tmpl](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/env.tmpl) to `.env` and substitute the default values with your
own usernames and passwords.

Install [Docker](https://docs.docker.com/get-docker/).

Run in the main RaiseWikibase folder:
```shell
docker-compose -f docker-compose.yml -f docker-compose.extra.yml up -d --scale wikibase_jobrunner=1
```
See more details at [Wikibase Release Pipeline](https://github.com/wmde/wikibase-release-pipeline/tree/wmde.2/example).

If it runs first time, it pulls the Wikibase Docker images. Then it builds, creates, starts, and attaches to containers for a service.
Check whether it's running using:
```shell
docker ps
```

If it's running, the output looks like this:
```shell
CONTAINER ID        IMAGE                                COMMAND                   CREATED              STATUS              PORTS                       NAMES
0cac985f00a5        wikibase/quickstatements:latest      "/bin/bash /entrypoi…"    About a minute ago   Up About a minute   0.0.0.0:9191->80/tcp        raisewikibase_quickstatements_1
2f277b599ea0        wikibase/wdqs:0.3.40                 "/entrypoint.sh /run…"    About a minute ago   Up About a minute                               raisewikibase_wdqs-updater_1
3d7e6462b290        wikibase/wdqs-frontend:latest        "/entrypoint.sh ngin…"    About a minute ago   Up About a minute   0.0.0.0:8282->80/tcp        raisewikibase_wdqs-frontend_1
ef945d05fc88        wikibase/wikibase:1.35-bundle        "/bin/bash /entrypoi…"    About a minute ago   Up About a minute   0.0.0.0:8181->80/tcp        raisewikibase_wikibase_1
10df54332657        wikibase/wdqs-proxy                  "/bin/sh -c \"/entryp…"   About a minute ago   Up About a minute   0.0.0.0:8989->80/tcp        raisewikibase_wdqs-proxy_1
37f34328b73f        wikibase/wdqs:0.3.40                 "/entrypoint.sh /run…"    About a minute ago   Up About a minute   9999/tcp                    raisewikibase_wdqs_1
9a1c8ddd8c89        wikibase/elasticsearch:6.5.4-extra   "/usr/local/bin/dock…"    About a minute ago   Up About a minute   9200/tcp, 9300/tcp          raisewikibase_elasticsearch_1
b640eaa556e3        mariadb:10.3                         "docker-entrypoint.s…"    About a minute ago   Up About a minute   127.0.0.1:63306->3306/tcp   raisewikibase_mysql_1
```

The logs can be viewed via:
```shell
docker-compose logs -f
```

Usually in less than a minute from the start you will see the messages from `wdqs-updater_1` in the logs: `INFO  o.w.q.r.t.change.RecentChangesPoller - Got no real changes` and `INFO  org.wikidata.query.rdf.tool.Updater - Sleeping for 10 secs`. The Wikibase front-end (http://localhost:8181) and query service (http://localhost:8282) are already available. Data filling can be started.

If you want to stop the Wikibase Docker, to remove all your uploaded data and to run a fresh Wikibase instance, use:
```shell
docker-compose down
docker volume prune
docker-compose up -d
```

See also [Wikibase/Docker](https://www.mediawiki.org/wiki/Wikibase/Docker).

### Wikibase Extensions

"Extensions let you customize how MediaWiki looks and works" is written in [Manual:Extensions](https://www.mediawiki.org/wiki/Manual:Extensions). Note that [Wikibase](https://wikiba.se) is itself an extension to the [Mediawiki](https://www.mediawiki.org/wiki/MediaWiki) software.

To add the datatype [Mathematical expression](https://www.wikidata.org/wiki/Help:Data_type#Mathematical_expression) (or simply `Math`) to a Wikibase instance, install the extension [Math](https://www.mediawiki.org/wiki/Extension:Math). An example is the property [defining formula](https://www.wikidata.org/entity/P2534).

See also [Extending Wikibase](https://wikiba.se/extend).

### Wikibase Data Model and RaiseWikibase functions

The [Wikibase Data Model](https://www.mediawiki.org/wiki/Wikibase/DataModel) is an ontology describing the structure of the data in Wikibase. A non-technical summary of the Wikibase model is available at [DataModel/Primer](https://www.mediawiki.org/wiki/Wikibase/DataModel/Primer). The initial [conceptual specification](https://www.mediawiki.org/wiki/Wikibase/DataModel)
for the Data Model was created by [Markus Krötzsch](http://korrekt.org/)
and [Denny Vrandečić](http://simia.net/wiki/Denny), with minor contributions by
Daniel Kinzler and [Jeroen De Dauw](https://www.EntropyWins.wtf). The Wikibase Data Model has been implemented by [Jeroen De Dauw](https://www.EntropyWins.wtf)
and Thiemo Kreuz as [Wikimedia Germany](https://wikimedia.de) employees for the [Wikidata project](https://wikidata.org/).

RaiseWikibase provides the functions for the [Wikibase Data Model](https://www.mediawiki.org/wiki/Wikibase/DataModel):
```python
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity
```

The functions `entity`, `claim`, `snak`, `description`, `alias`and `label` return the template dictionaries. So all basic operations with dictionaries in Python can be used. You can merge two dictionaries `X` and `Y` using `X | Y` (since Python 3.9), `{**X, **Y}` (since Python 3.5) and `X.update(Y)`.

Let's check the Wikidata entity [Q43229](https://www.wikidata.org/wiki/Q43229) with an English label 'organization'. You can create both English and German labels for the entity in a local Wikibase instance using RaiseWikibase:
```python
labels = {**label('en', 'organization'), **label('de', 'Organisation')}
```

Multiple English and German aliases can also be easily created:
```python
aliases = alias('en', ['organisation', 'org']) | alias('de', ['Org', 'Orga'])
```

Multilingual descriptions can be added:
```python
descriptions = description('en', 'social entity (not necessarily commercial)')
descriptions.update(description('de', 'soziale Struktur mit einem gemeinsamen Ziel'))
```

To add statements (claims), qualifiers and references, we need the `snak` function. To create a snak, we have to specify `property`, `datavalue`, `datatype` and `snaktype`. For example, if a Wikibase instance has the property with ID `P1`, a label `Wikidata ID` and datatype `external-id`, we can create a mainsnak with that property and the value 'Q43229':
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

If you need a claim with multiple values for one property, there are two opportunities. The first one is using the `extend` function on lists:
```python
claims1 = claim(prop='P1', mainsnak=mainsnak1, qualifiers=qualifiers1, references=references1)
claims2 = claim(prop='P1', mainsnak=mainsnak2, qualifiers=qualifiers2, references=references2)
claims1['P1'].extend(claims2['P1'])
```

The second option is using the `mainsnak` and `statement` functions:
```python
snak1 = snak(datatype='external-id', value='Q43229', prop='P1', snaktype='value')
snak2 = snak(datatype='external-id', value='Q5', prop='P1', snaktype='value')
mainsnak1 = mainsnak(prop='P1', snak=snak1, qualifiers=[], references=[])
mainsnak2 = mainsnak(prop='P1', snak=snak2, qualifiers=[], references=[])
statements = statement(prop='P1', mainsnaks=[mainsnak1, mainsnak2])
```

Note that the `claim` and `statement` functions return the same template dictionaries, but their input parameters are different. The `claim` function is useful when your claims have one value per property. Multiple values per property are easier to create using the `statement` function.

All ingredients for creating the JSON representation of an item are ready. The `entity` function does the job:
```python
item = entity(labels=labels, aliases=aliases, descriptions=descriptions, claims=claims, etype='item')
```
where `claims=claims` can be replaced by `claims=statements`.

If a property is created, the corresponding datatype has to be additionally specified:
```python
property = entity(labels=labels, aliases=aliases, descriptions=descriptions,
		  claims=claims, etype='property', datatype='string')
```

Note that these functions create only the dictionaries for the corresponding elements in the Wikibase Data Model. Writing into the database is performed using the `page` and `batch` functions.

### Creating entities and texts

To create one thousand items with the already created JSON representation of an item, use:
```python
from RaiseWikibase.raiser import batch
batch(content_model='wikibase-item', texts=[item for i in range(1000)])
```

Let `wtext` is a Python string representing a wikitext. Then, `wikitexts = [wtext for i in range(1000)]` is a list of wikitexts and `page_titles = ['wikitext' + str(i) for i in range(1000)]` is a list of the corresponding page titles. To create one thousand wikitexts in the main namespace, use:

```python
batch(content_model='wikitext', texts=wikitexts, namespace=0, page_title=page_titles)
```

The dictionary of [namespaces](https://www.mediawiki.org/wiki/Extension_default_namespaces) can be found here:
```python
from RaiseWikibase.datamodel import namespaces
```

The ID for the main namespace `namespaces['main']` is `0`.

Alternatively, the `page` function can be used directly. First, a connection object is created. The page function executes the necessary inserts, the changes are commited and the connection is closed:
```python
from RaiseWikibase.dbconnection import DBConnection
from RaiseWikibase.raiser import page
connection = DBConnection()
page(connection=connection, content_model=content_model,
     namespace=namespace, text=text, page_title=page_title, new=True)
connection.conn.commit()
connection.conn.close()
```

The argument `new` specifies whether the page is created (`new=True`) or edited (`new=False`). The `new` argument can be used in the `batch` function as well.

### Testing all datatypes

This section is moved to [docs](https://ub-mannheim.github.io/RaiseWikibase/quickstart/testing_datatypes). It describes testing all datatypes in a Wikibase instance and checking what kind of extensions they require.

### Compatibility with WikidataIntegrator and WikibaseIntegrator

[WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) and [WikibaseIntegrator](https://github.com/LeMyst/WikibaseIntegrator) are the wrappers of the [Wikibase API](https://www.mediawiki.org/wiki/Wikibase/API). A bot account is needed to start data filling with them. RaiseWikibase can create a bot account for a local Wikibase instance, save the login and password to a configuration file and read them back to a `config` dictionary:

```python
from RaiseWikibase.raiser import create_bot
from RaiseWikibase.settings import Settings
create_bot()
config = Settings()
```

The `config` dictionary can be used in WikibaseIntegrator for creating a login instance:
```python
from wikibaseintegrator import wbi_login
login_instance = wbi_login.Login(user=config.username, password=config.password)
```
and in WikidataIntegrator:
```python
from wikidataintegrator import wdi_login
login_instance = wdi_login.WDLogin(user=config.username, pwd=config.password)
```

You can also create the JSON representations of entities in WikidataIntegrator or WikibaseIntegrator and then fill them into a Wikibase instance using RaiseWikibase.
In WikibaseIntegrator you can create a `Item` object and use the `get_json` function:
```python
from wikibaseintegrator import WikibaseIntegrator
wbi = WikibaseIntegrator(login=login_instance)
item = wbi.item.get(entity_id='Q1003030')
ijson = item.get_json()
```

In WikidataIntegrator a `wdi_core.WDItemEngine` object can be created and the `get_wd_json_representation` function can be used:
```python
from wikidataintegrator import wdi_core
item = wdi_core.WDItemEngine(wd_item_id='Q1003030')
ijson = item.get_wd_json_representation()
```

The JSON representation of an entity can be uploaded into a Wikibase instance using the `batch` function in RaiseWikibase:
```python
from RaiseWikibase.raiser import batch
batch('wikibase-item', [ijson])
```

### Getting data from Wikidata and filling it into a Wikibase instance

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

## Performance analysis

The script [performance.py](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/performance.py) runs two performance experiments for creating the wikitexts and items. Run:
```shell
python3 performance.py
```

The variable [batch_lengths](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/performance.py#L39) is set by default to `[100]`. This means that the length of a batch in each experiment is `100`. Running both experiments in this case takes 80 seconds. You can set it to `[100, 200, 300]` in order to run multiple experiments with different batch lengths. In our experiments we used  `batch_lengths = [10000]`.

The script saves the CSV files with numeric values of results and creates the pdf files with figures in `./experiments/`.

| (1a) Wikitexts | (1b) Items |
|:------:|:------:|
| ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/exp1.png) | ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/exp2.png) |

The insert rates in pages per second are shown at Figure 1a for wikitexts and at Figure 1b for items. Every data point corresponds to a batch of ten thousands pages. At Figure 1a six different data points correspond to six repeated experiments. At Figure 1b two colors correspond to two repeated experiments and three shapes of a data point correspond to the three cases: 1) circle - each claim without a qualifier and without a reference, 2) x - each claim with one qualifier and without a reference, and 3) square - each claim with one qualifier and one reference.

To 'reproduce' Figures 1a and 1b, set [batch_lengths](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/performance.py#L39) to `[10000]`. Note that 'reproducibility' in this case does not mean that you will get the same values in the experiments as at Figures 1a and 1b. It means that you can get similar plots with the values specific for your hardware and software. Our analysis was performed using a workstation with 6-core Intel i5-8500T CPU @ 2.10GHz, 16GB RAM, SSD storage and running Debian 10.

## Creating a mini Wikibase instance with thousands of entities in a few minutes

The script [miniWikibase.py](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/miniWikibase.py) fills a fresh Wikibase instance with some structured and unstructured data in roughly 30 seconds. The data include 8400+ properties from [Wikidata](https://www.wikidata.org), two templates, a page with SPARQL examples, a page with a sidebar and modules. Check the folder `texts` containing unstructured data and add there your own data. Information about the Wikidata properties is queried through the [Wikidata endpoint](https://query.wikidata.org) and it takes a few seconds. Run:
```shell
python3 miniWikibase.py
```

| (2a) Main page | (2b) List of properties |
|:------:|:------:|
| ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/mini1.png) | ![alt text](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/experiments/mini2.png) |

Figure 2a shows the main page and Figure 2b shows a list of properties. If you run the script `miniWikibase.py` with the commented line 156, you will see only the property identifiers instead of the labels. You can either uncomment line 156 or run in shell `docker-compose down` and `docker-compose up -d`.

## Creating a mega Wikibase instance with millions of BERD entities in a few hours

The script [megaWikibase.py](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/megaWikibase.py) creates a knowledge graph with millions of BERD (Business, Economic and Related Data) entities from scratch. Before running it prepare the OpenCorporates dataset.
Download https://daten.offeneregister.de/openregister.db.gz. Unzip it and run in shell:
```shell
sqlite3 -header -csv handelsregister.db "select * from company;" > millions_companies.csv
```
Put `millions_companies.csv` to the main RaiseWikibase folder.

Run:
```shell
python3 megaWikibase.py
```

## Deployment in production

The setting above runs on localhost.

A [setup](https://github.com/needsone/my-wikibase) (and [this](https://stackoverflow.com/a/63397827)) for deployment using Nginx is provided by [Louis Poncet](https://github.com/needsone) ([personaldata.io](https://wiki.personaldata.io)).

## Paper

```
@inproceedings{RaiseWikibase2021,
author={Shigapov, Renat and Mechnich, J{\"o}rg and Schumm, Irene},
title={RaiseWikibase: {F}ast inserts into the {BERD} instance},
booktitle={The {S}emantic {W}eb: {ESWC} 2021 {S}atellite {E}vents},
year={2021},
publisher={Springer International Publishing},
pages={60--64},
doi={10.1007/978-3-030-80418-3\_11},
url={https://doi.org/10.1007/978-3-030-80418-3\_11}
}
```

[[DOI](https://doi.org/10.1007/978-3-030-80418-3_11)] [[preprint](https://openreview.net/pdf?id=87hp7LJDJE)] [[poster](https://ub-mannheim.github.io/RaiseWikibase/poster)]

## Acknowledgments

This work was funded by the Ministry of Science, Research and Arts of Baden-Württemberg through the project [Business and Economics Research Data Center Baden-Württemberg (BERD@BW)](https://www.berd-bw.de).

We thank [Jesper Zedlitz](https://github.com/jze) for his experiments explained at [the FactGrid blog](https://blog.factgrid.de/archives/2013) and for his open source code [wikibase-insert](https://github.com/jze/wikibase-insert).

## See also

[The official Wikibase website](https://wikiba.se), [Wikidata & Wikibase architecture documentation](https://wmde.github.io/wikidata-wikibase-architecture), [Strategy for the Wikibase Ecosystem](https://upload.wikimedia.org/wikipedia/commons/c/cc/Strategy_for_Wikibase_Ecosystem.pdf), the [posts about Wikibase](https://addshore.com/tag/wikibase) and [Wikidata](https://addshore.com/tag/wikidata/) by [Adam 'addshore' Shorland](https://addshore.com/about), a [Wikibase tutorial](https://stuff.coffeecode.net/2018/wikibase-workshop-swib18.html) by [Dan Scott](https://dscott.ca/#i), [Wikibase Install Basic Tutorial](https://semlab.io/howto/wikibase_basic) and [Wikibase for Research Infrastructure](https://medium.com/@thisismattmiller/wikibase-for-research-infrastructure-part-1-d3f640dfad34) by [Matt Miller](https://thisismattmiller.com/about), [Get your own copy of WikiData](http://wiki.bitplan.com/index.php/Get_your_own_copy_of_WikiData) by [Wolfgang Fahl](https://github.com/WolfgangFahl), [Transferring Wikibase data between wikis](https://wikibase.consulting/transferring-wikibase-data-between-wikis) by [Jeroen De Dauw](https://www.EntropyWins.wtf), [Putting Data into Wikidata using Software](http://baskauf.blogspot.com/2019/06/putting-data-into-wikidata-using.html) by [Steve Baskauf](https://github.com/baskaufs), [Vanderbilt Heard Library digital scholarship resources on Wikidata and Wikibase](https://heardlibrary.github.io/digital-scholarship/host/wikidata/), [Learning Wikibase](http://learningwikibase.com), [Wikibase Yearly Summary 2020](https://www.lehir.net/wikibase-yearly-summary-2020) and [Wikibase Yearly Summary 2021](https://www.lehir.net/wikibase-yearly-summary-2021).
