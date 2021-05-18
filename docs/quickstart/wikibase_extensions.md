---
layout: default
title: Wikibase Extensions
parent: QuickStart
nav_order: 2b
---
# Wikibase Extensions

"Extensions let you customize how MediaWiki looks and works" is written in [Manual:Extensions](https://www.mediawiki.org/wiki/Manual:Extensions). Note that [Wikibase](https://wikiba.se) is itself an extension to the [Mediawiki](https://www.mediawiki.org/wiki/MediaWiki) software.

Let's add extension [TemplateStyles](https://www.mediawiki.org/wiki/Extension:TemplateStyles). [Download](https://www.mediawiki.org/wiki/Special:ExtensionDistributor/TemplateStyles) and extract it to the folder `RaiseWikibase/extensions/`. Uncomment the [line 27](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/docker-compose.yml#L27) in [docker-compose.yml](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/docker-compose.yml) and the [lines 138-142](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/berd/LocalSettings.php.template#L138-L142) in [LocalSettings.php.template](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/berd/LocalSettings.php.template). RaiseWikibase uploads a css-file with the content model `'sanitized-css'` and the TemplateStyles extension is needed to deal with that content model. :warning: &nbsp; If you do not install the TemplateStyles extension and run the maintenance script `./maintenance/rebuildall.php` in the `*_wikibase_*` container, the error can occur: `The content model 'sanitized-css' is not registered on this wiki.`

To add the datatype [Mathematical expression](https://www.wikidata.org/wiki/Help:Data_type#Mathematical_expression) (or simply `Math`) to a Wikibase instance, install the extension [Math](https://www.mediawiki.org/wiki/Extension:Math). An example is the property [defining formula](https://www.wikidata.org/entity/P2534).

See also [Extending Wikibase](https://wikiba.se/extend).