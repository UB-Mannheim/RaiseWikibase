---
layout: default
title: Home
nav_order: 1
description: "RaiseWikibase: Fast inserts into a Wikibase instance"
permalink: /
---
## Home

RaiseWikibase is a Python tool for fast data filling and knowledge graph construction with Wikibase.

### Why do we need one more tool for data import into a Wikibase instance?

[Data import](https://www.mediawiki.org/wiki/Wikibase/Importing) into a Wikibase instance can be done

1. manually via GUI of a Wikibase instance, or
2. automatically via the Wikibase API and its wrappers.

The wrappers of the Wikibase API can insert roughly 1-6 entities per second. It is slow if millions of pages (wikitexts and entities) have to be uploaded. Instead of interacting with the Wikibase API, RaiseWikibase inserts data directly into MariaDB. This gives 10-100 times speed up.

### About RaiseWikibase

RaiseWikibase is developed within the project [Business & Economics Research Data Center](https://www.berd-bw.de) in order to create a knowledge graph of German companies with many millions of entities.

#### Publication

"RaiseWikibase: Fast inserts into the BERD instance" by Renat Shigapov, Jörg Mechnich and Irene Schumm, [ESWC 2021](https://2021.eswc-conferences.org) P&D, [preprint](https://openreview.net/pdf?id=87hp7LJDJE).

#### License

RaiseWikibase is distributed by an [MIT license](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/LICENSE).