<?php

$wgFooterIcons['poweredby']['wikibase'] = array(
		"src" => 'https://upload.wikimedia.org/wikipedia/commons/1/1c/Powered_by_Wikibase.svg',
		"url" => 'https://wikiba.se/',
		"alt" => 'Powered by Wikibase',
		"height" => '31',
		"width" => '88'
	);

$wgLogo = "./berd/logo_berdc_bw.jpg";

## Logs
## Save these logs inside the container
$wgDebugLogGroups = array(
	'resourceloader' => '/var/log/mediawiki/resourceloader.log',
	'exception' => '/var/log/mediawiki/exception.log',
	'error' => '/var/log/mediawiki/error.log',
);

$wgContentNamespaces = [ 120, 122, 0 ];

# Making the namespaces searched by default
$wgNamespacesToBeSearchedDefault[120] = true;
$wgNamespacesToBeSearchedDefault[122] = true;

## RC Age
# https://www.mediawiki.org/wiki/Manual:$wgRCMaxAge
# Items in the recentchanges table are periodically purged; entries older than this many seconds will go.
# The query service (by default) loads data from recent changes
# Set this to 1 year to avoid any changes being removed from the RC table over a shorter period of time.
$wgRCMaxAge = 365 * 24 * 3600;

# OAuth
wfLoadExtension( 'OAuth' );
$wgGroupPermissions['sysop']['mwoauthproposeconsumer'] = true;
$wgGroupPermissions['sysop']['mwoauthmanageconsumer'] = true;
$wgGroupPermissions['sysop']['mwoauthviewprivate'] = true;
$wgGroupPermissions['sysop']['mwoauthupdateownconsumer'] = true;

# CirrusSearch
$wgWBCSUseCirrus = true;
wfLoadExtension( 'Elastica' );
wfLoadExtension( 'CirrusSearch' );
wfLoadExtension( 'WikibaseCirrusSearch' );
$wgCirrusSearchServers = [ '${MW_ELASTIC_HOST}' ];
$wgSearchType = 'CirrusSearch';
#$wgWBRepoSettings['searchIndexProperties'] = ['P1020', 'P5699', 'P4'];
$wgWBRepoSettings['searchIndexTypes'] = [
	'string', 'external-id', 'url', 'wikibase-item', 'wikibase-property',
	'wikibase-lexeme', 'wikibase-form', 'wikibase-sense'
];

# Skin 'Timeless'
wfLoadSkin( 'Timeless' );
$wgDefaultSkin = 'timeless';

# UniversalLanguageSelector
wfLoadExtension( 'UniversalLanguageSelector' );

# cldr
wfLoadExtension( 'cldr' );

#EntitySchema
wfLoadExtension( 'EntitySchema' );

# Define property "formatterURL" for nice links to external identifiers
$wgWBRepoSettings['formatterUrlProperty'] = 'P2';
$wgWBRepoSettings['canonicalUriProperty'] = 'P3';

# Anonymous users are not allowed to edit pages and to create an account (another option is 'read')
$wgGroupPermissions['*']['edit'] = false;
$wgGroupPermissions['*']['createaccount'] = false;
$wgGroupPermissions['*']['createpage'] = false;
$wgGroupPermissions['*']['createtalk'] = false;
$wgGroupPermissions['*']['writeapi'] = false;

$wgWBRepoSettings['statementSections'] = array(
        'item' => array(
                'statements' => null,
                'identifiers' => array(
                        'type' => 'dataType',
                        'dataTypes' => array( 'external-id' ),
                ),
        ),
);

$wgLogo = "${DOLLAR}wgResourceBasePath/logo_berdc_bw.jpg";

wfLoadExtension( 'TemplateData' );

wfLoadExtension( 'Scribunto' );
$wgScribuntoDefaultEngine = 'luastandalone';

wfLoadExtension( 'SyntaxHighlight_GeSHi' );

$wgLocalisationUpdateDirectory = "$IP/cache";
$wgShowExceptionDetails = true;

$wgJobRunRate = 1.0;

# For debugging
$wgShowDebug = true;
$wgShowExceptionDetails = true;
$wgShowSQLErrors = true;
$wgDebugDumpSql  = true;
$wgShowDBErrorBacktrace = true;
$wgShowExceptionDetails = true;
$wgDevelopmentWarnings = true;

/*******************************/
/* Enable Federated properties */
/*******************************/
#$wgWBRepoSettings['federatedPropertiesEnabled'] = true;

/*******************************/
/* Enables ConfirmEdit Captcha */
/*******************************/
#wfLoadExtension( 'ConfirmEdit/QuestyCaptcha' );
#$wgCaptchaQuestions = [
#  'What animal' => 'dog',
#];

#$wgCaptchaTriggers['edit']          = true;
#$wgCaptchaTriggers['create']        = true;
#$wgCaptchaTriggers['createtalk']    = true;
#$wgCaptchaTriggers['addurl']        = true;
#$wgCaptchaTriggers['createaccount'] = true;
#$wgCaptchaTriggers['badlogin']      = true;

/*******************************/
/* Disable UI error-reporting  */
/*******************************/
#ini_set( 'display_errors', 0 );
