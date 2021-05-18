---
layout: default
title: Testing datatypes
parent: QuickStart
nav_order: 2e
---
# Testing datatypes

The goal of this section is to test all datatypes in a Wikibase instance and to check what kind of extensions they require.

Two main content models in a Wikibase instance are items and properties. In contrast to items, every property has a specific [datatype](https://www.wikidata.org/wiki/Help:Data_type). Many datatypes are supported by default. Some of the datatypes need special extensions and configuration.

The datatype [Mathematical expression](https://www.wikidata.org/wiki/Help:Data_type#Mathematical_expression) needs [Math extension](https://www.mediawiki.org/wiki/Extension:Math).

The datatype [Commons Media](https://www.wikidata.org/wiki/Help:Data_type#Commons_media) allows to use images from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page). To render an image in a browser, the line `${DOLLAR}wgUseInstantCommons = true;` has to be added to `LocalSettings.php.template`.

The datatype `Local Media` needs the [WikibaseLocalMedia extension](https://github.com/ProfessionalWiki/WikibaseLocalMedia). Take care of permissions, see [issue 7](https://github.com/ProfessionalWiki/WikibaseLocalMedia/issues/7). First, a file needs to be uploaded to the file store, specified by [$wgUploadDirectory](https://www.mediawiki.org/wiki/Manual:$wgUploadDirectory). To make that happen, we need to allow file uploads. Add the following lines to `LocalSettings.php.template`:
```
${DOLLAR}wgEnableUploads = true;
${DOLLAR}wgGroupPermissions['user']['upload'] = false;
${DOLLAR}wgGroupPermissions['user']['reupload'] = false;
${DOLLAR}wgGroupPermissions['user']['reupload-shared'] = false;
```
If you still cannot upload a file, check access permissions for the folder specified by [$wgUploadDirectory](https://www.mediawiki.org/wiki/Manual:$wgUploadDirectory). Check also [Configuring file uploads](https://www.mediawiki.org/wiki/Manual:Configuring_file_uploads).

The datatype [Musical Notation](https://www.wikidata.org/wiki/Help:Data_type#Musical_Notation) needs the [Score extension](https://www.mediawiki.org/wiki/Extension:Score). Add the following lines to `LocalSettings.php.template`:
```
wfLoadExtension( 'Score' );
${DOLLAR}wgScoreTrim = true;
${DOLLAR}wgImageMagickConvertCommand = '/usr/bin/convert';
${DOLLAR}wgShellRestrictionMethod = 'firejail';
${DOLLAR}wgMusicalNotationEnableWikibaseDataType = true;
```
BUT there is still an issue [T257066](https://phabricator.wikimedia.org/T257066), so don't use musical notation at the moment.

The datatype [Lexeme](https://www.wikidata.org/wiki/Help:Data_type#Lexemes) requires the [WikibaseLexeme extension](https://www.mediawiki.org/wiki/Extension:WikibaseLexeme). Add `wfLoadExtension( 'WikibaseLexeme' );` to `LocalSettings.php.template`.

The datatype [Form](https://www.wikidata.org/wiki/Help:Data_type#Forms) requires the [Form extension](https://www.mediawiki.org/wiki/Extension:Form). Add `wfLoadExtension( 'Form' );` to `LocalSettings.php.template`.

To embed a map into a page instead of showing a link to a map, the [Kartographer extension](https://www.mediawiki.org/wiki/Extension:Kartographer) is needed. To run Kartographer, the [JsonConfig extension](https://www.mediawiki.org/wiki/Extension:JsonConfig) has to be installed. Then, the variable for a tile server `${DOLLAR}wgKartographerMapServer` has to be changed to a non-Mediawiki one. But even this is still not enough, see [T271617](https://phabricator.wikimedia.org/T271617) and [T259868](https://phabricator.wikimedia.org/T259868). So currently a map is not embedded.

To perform the following test, you need to download all those extensions into `RaiseWikibase/extensions/`, mount them using `docker-compose.yml` and configure them in `LocalSettings.php.template`. Then run `miniWikibase.py` in order to upload the Wikidata properties. The following example creates an item with 18 claims corresponding to 18 properties with different datatypes.

```python
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity
from RaiseWikibase.raiser import batch
from RaiseWikibase.dbconnection import DBConnection

localmedia = entity(labels=label('en', 'local media'), etype='property', datatype='localMedia')
batch('wikibase-property', [localmedia])

labels = label('en', 'Entity with many datatypes')

c = DBConnection()
code = c.search_text_str('postal code', True)[0] # string
formula = c.search_text_str('defining formula', True)[0] # math
wid = c.search_text_str('Wikidata ID', True)[0] # external-id
url = c.search_text_str('official website', True)[0] # url
image = c.search_text_str('image', True)[0] # commonsMedia
geoshape = c.search_text_str('geoshape', True)[0] # geo-shape
musicnot = c.search_text_str('musical motif', True)[0] # musical-notation
tabdata = c.search_text_str('based on tabular data', True)[0] # tabular-data
lmedia = c.search_text_str('local media', True)[0] # localMedia
country = c.search_text_str('country', True)[0] # wikibase-item
iprop = c.search_text_str('inverse property', True)[0] # wikibase-property
inception = c.search_text_str('inception', True)[0] # time
nickname = c.search_text_str('nickname', True)[0] # monolingualtext
visitors = c.search_text_str('visitors per year', True)[0] # quantity
coordinates = c.search_text_str('coordinate location', True)[0] # globe-coordinate
lexeme = c.search_text_str('subject lexeme', True)[0] # wikibase-lexeme
altform = c.search_text_str('alternative form', True)[0] # wikibase-form
specsense = c.search_text_str('specified by sense', True)[0] # wikibase-sense
c.conn.close()

claims = {**claim(prop=code,
                  mainsnak=snak(datatype='string',
                                value='69001',
                                prop=code,
                                snaktype='value')),
          **claim(prop=formula,
                  mainsnak=snak(datatype='math',
                                value='E = m c^2',
                                prop=formula,
                                snaktype='value')),
          **claim(prop=wid,
                  mainsnak=snak(datatype='external-id',
                                value='Q43229',
                                prop=wid,
                                snaktype='value')),
          **claim(prop=url,
                  mainsnak=snak(datatype='url',
                                value='https://www.berd-bw.de',
                                prop=url,
                                snaktype='value')),
          **claim(prop=image,
                  mainsnak=snak(datatype='commonsMedia',
                                value='Heidelberg,_Neckar_River,_Old_Bridge,_Castle.jpg',
                                prop=image,
                                snaktype='value')),
          **claim(prop=lmedia,
                  mainsnak=snak(datatype='localMedia',
                                value='test.jpg',
                                prop=lmedia,
                                snaktype='value')),
          **claim(prop=geoshape,
                  mainsnak=snak(datatype='geo-shape',
                                value='Data:Germany.map',
                                prop=geoshape,
                                snaktype='value')),
          **claim(prop=musicnot,
                  mainsnak=snak(datatype='musical-notation',
                                value="{\\clef treble \\key c \\minor \\set Staff.midiInstrument=#\"violin\"\\tempo\"Allegro con brio\"2=108\\time 2/4r8g'\\ff[g'g']ees'2\\fermata r8f'[f'f']d'2~d'\\fermata}",
                                prop=musicnot,
                                snaktype='value')),
          **claim(prop=tabdata,
                  mainsnak=snak(datatype='tabular-data',
                                value='Data:Commons Milestones.tab',
                                prop=tabdata,
                                snaktype='value')),
          **claim(prop=country,
                  mainsnak=snak(datatype='wikibase-item',
                                value='Q1',
                                prop=country,
                                snaktype='value')),
          **claim(prop=iprop,
                  mainsnak=snak(datatype='wikibase-property',
                                value='P1',
                                prop=iprop,
                                snaktype='value')),
          **claim(prop=inception,
                  mainsnak=snak(datatype='time',
                                value=['+2021-03-26T00:00:00Z', 0, 11,
                                       'http://www.wikidata.org/entity/Q1985727'],
                                prop=inception,
                                snaktype='value')),
          **claim(prop=nickname,
                  mainsnak=snak(datatype='monolingualtext',
                                value=['Raise Wikibase', 'en'],
                                prop=nickname,
                                snaktype='value')),
          **claim(prop=visitors,
                  mainsnak=snak(datatype='quantity',
                                value=['50', '1', '70', '40'],
                                prop=visitors,
                                snaktype='value')),
          **claim(prop=coordinates,
                  mainsnak=snak(datatype='globe-coordinate',
                                value=[27.988055555556,
                                       86.925277777778,
                                       0.00027777777777778,
                                       'http://www.wikidata.org/entity/Q2'],
                                prop=coordinates,
                                snaktype='value')),
          **claim(prop=lexeme,
                  mainsnak=snak(datatype='wikibase-lexeme',
                                value='L1',
                                prop=lexeme,
                                snaktype='value')),
          **claim(prop=altform,
                  mainsnak=snak(datatype='wikibase-form',
                                value='L1-F1',
                                prop=altform,
                                snaktype='value')),
          **claim(prop=specsense,
                  mainsnak=snak(datatype='wikibase-sense',
                                value='L1-S1',
                                prop=specsense,
                                snaktype='value')),
         }

item = entity(labels=labels, claims=claims, etype='item')
batch('wikibase-item', [item])
```

Check the item at http://localhost:8181/wiki/Special:RecentChanges. Can you see all 18 claims at the item page?

The changes in `LocalSettings.php.template` are:
```
wfLoadExtension( 'Math' );
wfLoadExtension( 'WikibaseLocalMedia' );
wfLoadExtension( 'WikibaseLexeme' );
wfLoadExtension( 'Score' );
wfLoadExtension( 'Form' );
wfLoadExtension( 'JsonConfig' );
wfLoadExtension( 'Kartographer' );
${DOLLAR}wgEnableUploads = true;
${DOLLAR}wgGroupPermissions['user']['upload'] = false;
${DOLLAR}wgGroupPermissions['user']['reupload'] = false;
${DOLLAR}wgGroupPermissions['user']['reupload-shared'] = false;
${DOLLAR}wgScoreTrim = true;
${DOLLAR}wgImageMagickConvertCommand = '/usr/bin/convert';
${DOLLAR}wgShellRestrictionMethod = 'firejail';
${DOLLAR}wgMusicalNotationEnableWikibaseDataType = true;
${DOLLAR}wgUseInstantCommons = true;
${DOLLAR}wgKartographerMapServer = "https://tile.openstreetmap.org";
```

The changes in `docker-compose.yml` are:
```
      - ./extensions/Math:/var/www/html/extensions/Math
      - ./extensions/WikibaseLocalMedia:/var/www/html/extensions/WikibaseLocalMedia
      - ./extensions/Score:/var/www/html/extensions/Score
      - ./extensions/WikibaseLexeme:/var/www/html/extensions/WikibaseLexeme
      - ./extensions/Form:/var/www/html/extensions/Form
      - ./extensions/Kartographer:/var/www/html/extensions/Kartographer
      - ./extensions/JsonConfig:/var/www/html/extensions/JsonConfig
```

Conclusions: 'in theory' a Wikibase instance offers 18 datatypes, but not all of them work out of the box. 'In practice' even if I follow all the instructions at the extension pages at Mediawiki and look at many issues at Phabricator, there are still some problems with maps, musical notations, lexemes, forms and senses. See [T278674](https://phabricator.wikimedia.org/T278674).