# Poster

* [Title](https://www.wikidata.org/wiki/Property:P1476): **RaiseWikibase: Fast inserts into the BERD instance**
* [Authors](https://www.wikidata.org/wiki/Property:P50): **[Renat Shigapov](https://github.com/shigapov), [Jörg Mechnich](https://github.com/jmechnich) & [Irene Schumm](https://github.com/libschumm)**
* [Abstract](https://schema.org/abstract): _The open-source tool [RaiseWikibase](https://github.com/UB-Mannheim/RaiseWikibase) for fast [data import](https://www.mediawiki.org/wiki/Wikibase/Importing) and [knowledge graph](https://en.wikipedia.org/wiki/Knowledge_graph) construction with [Wikibase](https://www.wikiba.se) is presented._
* [BERD@BW](https://www.berd-bw.de): Business & Economics Research Data Center [Baden-Württemberg](https://www.wikidata.org/wiki/Q985)

![alt text](/assets/images/mediawiki_wb_import.png)

## Motivation

* German company data is fragmented over providers, registers & time spans.
* To handle with that, we create the [BERD knowledge graph](https://www.berd-bw.de/knowledge-graph) for German company data.
* [Wikibase](https://www.wikiba.se) is chosen for implementation, but [data import](https://www.mediawiki.org/wiki/Wikibase/Importing) via the [Wikibase API](https://www.wikidata.org/wiki/Q106877126) is a bit slow:

| the Wikibase frontend | the Wikibase API | MariaDB |
|:------:|:------:|:------:|
| manual page creation | [WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) | [wikibase-insert](https://github.com/jze/wikibase-insert) |
|        | [WikibaseIntegrator](https://github.com/LeMyst/WikibaseIntegrator) | [RaiseWikibase](https://github.com/UB-Mannheim/RaiseWikibase) |
|        | [wikibase-cli](https://github.com/maxlath/wikibase-cli) |  |
|        | [WikidataToolkit](https://github.com/Wikidata/Wikidata-Toolkit) |  |
|        | [Pywikibot](https://github.com/wikimedia/pywikibot) |  |
|        | [QuickStatements](https://github.com/magnusmanske/quickstatements) |  |
|**less than 1 page per second**| **1-6 pages per second** | **100-300 pages per second** |

## RaiseWikibase

* Open-source [Python](https://www.wikidata.org/wiki/Q28865) tool.
* Adapted to [Wikibase Docker Image](https://github.com/wmde/wikibase-docker) "1.35".
* Connects to MariaDB via the [mysqlclient](https://github.com/PyMySQL/mysqlclient) library.

## Main functions

The [page](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/RaiseWikibase/raiser.py#L14-L80) function executes inserts into the database but does not commit them:
```python
from RaiseWikibase.dbconnection import DBConnection
from RaiseWikibase.raiser import page
connection = DBConnection()
page(connection=connection, content_model=content_model,
     namespace=namespace, text=text, page_title=page_title, new=True)
connection.conn.commit()
connection.conn.close()
```

Multiple [page](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/RaiseWikibase/raiser.py#L14-L80) functions are wrapped into a transaction inside the [batch](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/RaiseWikibase/raiser.py#L83-L110) function:
```python
from RaiseWikibase.raiser import batch
batch(content_model='wikibase-item', texts=[item for i in range(1000)])
```
where `item` is the JSON representation of an item created using the [entity](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/RaiseWikibase/datamodel.py#L198-L225) function.

## Performance

* The insert rate decreases approximately linearly with increasing number of characters per wikitext and with increasing number of claims per item.
* Small pages are uploaded at rates of 250-350 wikitexts per second and 220-280 items per second.

| Wikitexts | Items |
|:------:|:------:|
| ![alt text](/assets/images/exp1.png) | ![alt text](/assets/images/exp2.png) |

## Configuration

* The folder [texts](https://github.com/UB-Mannheim/RaiseWikibase/tree/main/texts) contains [templates](https://www.wikidata.org/wiki/Q11266439), [modules](https://www.wikidata.org/wiki/Q15184295) and other [unstructured data](https://www.wikidata.org/wiki/Q1141900).
* Modify them and add your own files to [texts](https://github.com/UB-Mannheim/RaiseWikibase/tree/main/texts).
* Run the function [fill_texts](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/miniWikibase.py#L108-L134).

![alt text](/assets/images/main_page.png)

## Federated properties

* [Federated properties](https://doc.wikimedia.org/Wikibase/master/php/md_docs_components_repo-federated-properties.html) are under development in [Wikimedia Germany](https://www.wikimedia.de).
* Therefore, run the script [miniWikibase.py](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/miniWikibase.py).
* It creates all properties from [Wikidata](https://www.wikidata.org) in a local Wikibase instance.

![alt text](/assets/images/properties.png)

## Creating a knowledge graph

* Download [OffeneRegister](https://offeneregister.de) dataset donated to [OKFD](https://okfn.de) by [OpenCorporates](https://opencorporates.com).
* Semantic annotator [bbw](https://github.com/UB-Mannheim/bbw) annotates the tables automatically using [Wikidata](https://www.wikidata.org).
* Run [megaWikibase.py](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/megaWikibase.py).

![alt text](/assets/images/item.png)

## Conclusions

|:------:|:------:|
| 1. Clone [RaiseWikibase](https://github.com/UB-Mannheim/RaiseWikibase) and adapt the files for your use case. <br/> <br/> 2. Build fast your own [Wikibase](https://www.wikiba.se) [knowledge graph](https://en.wikipedia.org/wiki/Knowledge_graph). <br/> <br/> 3. Join the [Wikibase Ecosystem](https://upload.wikimedia.org/wikipedia/commons/c/cc/Strategy_for_Wikibase_Ecosystem.pdf).| ![alt text](/assets/images/WikibaseEcosystem.png) |


## See also

[Wikibase](https://www.wikiba.se){: .btn .btn-green .mr-2 }
[Wikidata](https://www.wikidata.org){: .btn .btn-green .mr-2 }
[BERD@BW](https://www.berd-bw.de){: .btn .btn-purple .mr-2 }
[bbw](https://github.com/UB-Mannheim/bbw){: .btn .btn-purple .mr-2 }
[QuickStart](https://ub-mannheim.github.io/RaiseWikibase/quickstart/){: .btn .btn-blue .mr-2 }
[RaiseWikibase](https://github.com/UB-Mannheim/RaiseWikibase){: .btn .btn-blue }
