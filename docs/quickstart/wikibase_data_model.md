---
layout: default
title: Wikibase Data Model & RaiseWikibase functions
parent: QuickStart
nav_order: 2c
---
# Wikibase Data Model & RaiseWikibase functions

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