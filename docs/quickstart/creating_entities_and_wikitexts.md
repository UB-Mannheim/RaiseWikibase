---
layout: default
title: Creating entities & wikitexts
parent: QuickStart
nav_order: 2d
---
# Creating entities & wikitexts

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