---
layout: default
title: Compatibility with WikidataIntegrator & WikibaseIntegrator
parent: QuickStart
nav_order: 2f
---
# Compatibility with WikidataIntegrator & WikibaseIntegrator

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
login_instance = wbi_login.Login(user=config.username, pwd=config.password)
```
and in WikidataIntegrator:
```python
from wikidataintegrator import wdi_login
login_instance = wdi_login.WDLogin(user=config.username, pwd=config.password)
```

You can also create the JSON representations of entities in WikidataIntegrator or WikibaseIntegrator and then fill them into a Wikibase instance using RaiseWikibase. In WikibaseIntegrator you can create a `wbi_core.ItemEngine` object and use the `get_json_representation`  function:
```python
from wikibaseintegrator import wbi_core
item = wbi_core.ItemEngine(item_id='Q1003030')
ijson = item.get_json_representation()
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