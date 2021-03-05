<?php
/**
 * Example:
 *
 * createOAuthConsumer.php
 *   --callbackIsPrefix
 *   --callbackUrl="https://foourl"
 *   --description="Application description"
 *   --grants="editprotected"
 *   --grants="createaccount"
 *   --name="Application name"
 *   --user="Admin"
 *   --version="0.2"
 *   --wiki=default
 *   --approve
 *
 * You can optionally output successful results as json using --jsonOnSuccess
 */

namespace MediaWiki\Extensions\OAuth;

use MediaWiki\Extensions\OAuth\Backend\Consumer;
use MediaWiki\Extensions\OAuth\Backend\Utils;
use MediaWiki\Extensions\OAuth\Control\ConsumerSubmitControl;

/**
 * @ingroup Maintenance
 */

if ( getenv( 'MW_INSTALL_PATH' ) ) {
	$IP = getenv( 'MW_INSTALL_PATH' );
} else {
	$IP = __DIR__ . '/../../..';
}

require_once "$IP/maintenance/Maintenance.php";

class CreateOAuthConsumer extends \Maintenance {
	public function __construct() {
		parent::__construct();
		$this->addDescription( "Create an OAuth consumer" );
		$this->addOption( 'user', 'User to run the script as', true, true );
		$this->addOption( 'name', 'Application name', true, true );
		$this->addOption( 'description', 'Application description', true, true );
		$this->addOption( 'version', 'Application version', true, true );
		$this->addOption( 'callbackUrl', 'Callback URL', true, true );
		$this->addOption(
			'callbackIsPrefix',
			'Allow a consumer to specify a callback in requests',
			true
		);
		$this->addOption( 'grants', 'Grants', true, true, false, true );
		$this->addOption( 'jsonOnSuccess', 'Output successful results as JSON' );
		$this->addOption( 'approve', 'Accept the consumer' );
		$this->requireExtension( "OAuth" );
	}

	public function execute() {
		$user = \User::newFromName( $this->getOption( 'user' ) );
		if ( $user->isAnon() ) {
			$this->fatalError( 'User must be registered' );
		}
		if ( $user->getEmail() === '' ) {
			$this->fatalError( 'User must have an email' );
		}

		$data = [
			'action' => 'propose',
			'name'         => $this->getOption( 'name' ),
			'version'      => $this->getOption( 'version' ),
			'description'  => $this->getOption( 'description' ),
			'callbackUrl'  => $this->getOption( 'callbackUrl' ),
			'oauthVersion' => 1,
			'callbackIsPrefix' => $this->hasOption( 'callbackIsPrefix' ),
			'grants' => '["' . implode( '","', $this->getOption( 'grants' ) ) . '"]',
			'granttype' => 'normal',
			'ownerOnly' => false,
			'oauth2IsConfidential' => false, // only support OAUth 1 for now
			'oauth2GrantTypes' => null, // only support OAUth 1 for now
			'email' => $user->getEmail(),
			'wiki' => '*', // All wikis
			'rsaKey' => '', // Generate a key
			'agreement' => true,
			'restrictions' => \MWRestrictions::newDefault(),
		];

		$context = \RequestContext::getMain();
		$context->setUser( $user );

		$dbw = Utils::getCentralDB( DB_MASTER );
		$control = new ConsumerSubmitControl( $context, $data, $dbw );
		$status = $control->submit();

		if ( !$status->isGood() ) {
			$this->fatalError( $status->getMessage()->text() );
		}

		/** @var Consumer $cmr */
		// @phan-suppress-next-line PhanTypeArraySuspiciousNullable
		$cmr = $status->value['result']['consumer'];

		if ( $this->hasOption( 'approve' ) ) {
			$data = [
				'action' => 'approve',
				'consumerKey'  => $cmr->getConsumerKey(),
				'reason'       => 'Approved by maintenance script',
				'changeToken'  => $cmr->getChangeToken( $context ),
			];
			$control = new ConsumerSubmitControl( $context, $data, $dbw );
			$approveStatus = $control->submit();
		}

		$outputData = [
			'created' => true,
			'id' => $cmr->getId(),
			'name' => $cmr->getName(),
			'key' => $cmr->getConsumerKey(),
			'secret' => Utils::hmacDBSecret( $cmr->getSecretKey() ),
		];

		if ( isset( $approveStatus ) ) {
			$outputData['approved'] = $approveStatus->isGood() ?
				1 : $approveStatus->getWikiText( false, false, 'en' );
		}

		if ( $this->hasOption( 'jsonOnSuccess' ) ) {
			$this->output( json_encode( $outputData ) );
		} else {
			foreach ( $outputData as $key => $value ) {
				$this->output( $key . ': ' . $value . PHP_EOL );
			}
		}
	}
}

$maintClass = CreateOAuthConsumer::class;
require_once RUN_MAINTENANCE_IF_MAIN;

