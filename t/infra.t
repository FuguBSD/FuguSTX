#!/usr/bin/env perl
# ex:ts=8 sw=4:
# Guards for the scripts/infra task runner.
#
# The tests cover the stop decision of the pre-apply forecast check
# (TRN-BUDGET-1), the bucket versioning check (COR-BUCKETS-2), and the
# destroy and report decisions of the watchdog. Stub scw, curl, and
# tofu commands on the PATH stand in place of the platform.

use v5.36;
use Test::More;
use File::Temp qw(tempdir);
use FindBin    qw($RealBin);
use POSIX      qw(strftime);

my $root = "$RealBin/..";
my $dir  = tempdir( CLEANUP => 1 );
my $stub = "$dir/bin";
mkdir $stub or die $!;

# _write($path, $content, %options):
#	Write one file. The mode 0755 makes a stub executable.
sub _write ( $path, $content, %options )
{
	open my $fh, '>', $path or die "write $path: $!";
	print $fh $content;
	close $fh;
	chmod 0755, $path if $options{executable};

	return;
}

# The scw stub routes on its arguments and reads fixture files. A tofu
# destroy leaves a marker, and the server list honors it, so the
# watchdog's removal confirmation sees an empty zone.
_write( "$stub/scw", <<'STUB', executable => 1 );
#!/usr/bin/env perl
use v5.36;
open my $log, '>>', $ENV{STX_LOG} or die $!;
say $log "scw @ARGV";
close $log;
my $argv = "@ARGV";
sub emit ($path) { open my $fh, '<', $path or die $!; print <$fh>; exit 0 }
if ( $argv =~ /instance server list/ ) {
	if ( -f "$ENV{STX_STATE}/destroyed" ) { say '[]'; exit 0 }
	emit("$ENV{STX_FIX}/servers.json");
}
if ( $argv =~ /instance (?:ip|volume) list/ ) { say '[]';              exit 0 }
if ( $argv =~ /iam application list/ )        { say '[{"id":"app-1"}]'; exit 0 }
if ( $argv =~ /iam api-key list/ )            { say '[]';              exit 0 }
if ( $argv =~ /iam api-key delete/ )          { say '{}';              exit 0 }
die "scw stub: no route for: $argv\n";
STUB

# The curl stub serves the billing read, the heartbeat head, and the
# bucket versioning read.
_write( "$stub/curl", <<'STUB', executable => 1 );
#!/usr/bin/env perl
use v5.36;
open my $log, '>>', $ENV{STX_LOG} or die $!;
say $log "curl @ARGV";
close $log;
my $argv = "@ARGV";
my ($url) = grep { m{^https://} } @ARGV;
sub emit ($path) { open my $fh, '<', $path or die $!; print <$fh>; exit 0 }
emit("$ENV{STX_FIX}/consumption.json") if $url =~ /billing/;
emit("$ENV{STX_FIX}/heartbeat.txt")    if $url =~ m{/runs/};
if ( $url =~ m{https://([a-z-]+)\.s3.*\?versioning} ) {
	emit("$ENV{STX_FIX}/versioning-$1.xml");
}
die "curl stub: no route for: $url\n";
STUB

_write( "$stub/tofu", <<'STUB', executable => 1 );
#!/usr/bin/env perl
use v5.36;
open my $log, '>>', $ENV{STX_LOG} or die $!;
say $log "tofu @ARGV";
close $log;
if ( grep { $_ eq 'destroy' } @ARGV ) {
	open my $marker, '>', "$ENV{STX_STATE}/destroyed" or die $!;
	close $marker;
}
exit 0;
STUB

# _run($command, %options):
#	Run one scripts/infra command against fresh fixtures. Return
#	the output, the exit status, and the stub call log.
sub _run ( $command, %options )
{
	my $fixtures = tempdir( CLEANUP => 1 );
	my $state    = tempdir( CLEANUP => 1 );
	my $log      = "$fixtures/calls.log";
	_write( $log, '' );
	_write( "$fixtures/$_", $options{fixtures}{$_} )
	    for keys %{ $options{fixtures} // {} };

	local $ENV{PATH}                        = "$stub:$ENV{PATH}";
	local $ENV{STX_LOG}                     = $log;
	local $ENV{STX_FIX}                     = $fixtures;
	local $ENV{STX_STATE}                   = $state;
	local $ENV{SCW_ACCESS_KEY}              = 'SCWFAKE';
	local $ENV{SCW_SECRET_KEY}              = 'fake-secret';
	local $ENV{SCW_DEFAULT_PROJECT_ID}      = 'proj-ours';
	local $ENV{SCW_DEFAULT_ORGANIZATION_ID} = 'org-1';

	my $output = qx{$^X $root/scripts/infra $command 2>&1};
	my $status = $? >> 8;
	open my $fh, '<', $log or die $!;
	local $/ = undef;
	my $calls = <$fh>;
	close $fh;

	return ( $output, $status, $calls );
}

# _rfc3339($epoch) and _http_date($epoch):
#	The two date shapes of the fixtures.
sub _rfc3339 ($epoch) { strftime( '%Y-%m-%dT%H:%M:%SZ', gmtime $epoch ) }

sub _http_date ($epoch)
{
	my @days   = qw(Sun Mon Tue Wed Thu Fri Sat);
	my @months = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);
	my ( $sec, $min, $hour, $mday, $mon, $year, $wday ) = gmtime $epoch;

	return sprintf '%s, %02d %s %04d %02d:%02d:%02d GMT',
	    $days[$wday], $mday, $months[$mon], $year + 1900,
	    $hour, $min, $sec;
}

# _consumption($ours, $age_hours):
#	One billing read fixture: our project, plus an other project
#	that the sum must exclude.
sub _consumption ( $ours, $age_hours )
{
	my $updated = _rfc3339( time - $age_hours * 3600 );

	return <<"EOF";
{"consumptions":[
  {"project_id":"proj-ours","value":{"units":$ours,"nanos":0}},
  {"project_id":"proj-other","value":{"units":250,"nanos":0}}
],"updated_at":"$updated"}
EOF
}

# _server($age_minutes, %tags):
#	One server list fixture with one server.
sub _server ( $age_minutes, %tags )
{
	my $created = _rfc3339( time - $age_minutes * 60 );
	my $tags    = join ',', map {qq("$_=$tags{$_}")} sort keys %tags;

	return <<"EOF";
[{"name":"stx.prod.train","commercial_type":"H100-1-80G",
  "state":"running","creation_date":"$created","tags":[$tags]}]
EOF
}

my %train_tags = (
	'stx:stack'     => 'train',
	'stx:managed'   => 'true',
	'stx:lifecycle' => 'ephemeral',
	'stx:run-id'    => 'run-1',
);

subtest 'the forecast check goes under the budget' => sub {
	my ( $output, $status ) = _run(
		'forecast --price 2.87 --hours 4',
		fixtures => { 'consumption.json' => _consumption( 10, 1 ) },
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/forecast: go:/, 'the go verdict' );
	unlike( $output, qr/250/, 'an other project does not count' );
};

subtest 'the forecast check stops over the budget' => sub {
	my ( $output, $status ) = _run(
		'forecast --price 2.87 --hours 4',
		fixtures => { 'consumption.json' => _consumption( 295, 1 ) },
	);
	is( $status, 1, 'exit 1' );
	like( $output, qr/forecast: stop:.*passes the EUR 300/, 'the reason' );
};

subtest 'the forecast check stops on a stale read' => sub {
	my ( $output, $status ) = _run(
		'forecast --price 2.87 --hours 4',
		fixtures => { 'consumption.json' => _consumption( 10, 7 ) },
	);
	is( $status, 1, 'exit 1' );
	like( $output, qr/forecast: stop:.*hours old/, 'the reason' );
};

subtest 'a forecast never assumes a run cheaper than one hour' => sub {
	my ( $output, $status ) = _run(
		'forecast --price 2.00 --hours 0.25',
		fixtures => { 'consumption.json' => _consumption( 10, 1 ) },
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/EUR 2\.00 forecast/, 'one full hour is priced' );
};

# A versioning fixture ends with the HTTP code that curl -w appends.
my $enabled =
    "<VersioningConfiguration><Status>Enabled</Status></VersioningConfiguration>\n200";
my %versioning_ok = (
	'versioning-stx-corpus.xml'      => $enabled,
	'versioning-stx-evalcorpus.xml'  => $enabled,
	'versioning-stx-artifacts.xml'   => $enabled,
	'versioning-stx-checkpoints.xml' => "<VersioningConfiguration/>\n200",
);

subtest 'the status versioning check passes on COR-BUCKETS-2' => sub {
	my ( $output, $status ) = _run(
		'status',
		fixtures => { 'servers.json' => '[]', %versioning_ok },
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/stx-corpus versioning Enabled: ok/, 'corpus on' );
	like( $output, qr/stx-checkpoints versioning off: ok/,
		'checkpoints off' );
};

subtest 'the status versioning check fails on a mismatch' => sub {
	my ( $output, $status ) = _run(
		'status',
		fixtures => {
			'servers.json' => '[]',
			%versioning_ok,
			'versioning-stx-checkpoints.xml' => $enabled,
		},
	);
	is( $status, 1, 'exit 1' );
	like( $output, qr/stx-checkpoints.*MISMATCH/, 'the mismatch names' );
};

subtest 'a suspended checkpoint bucket counts as off' => sub {
	my ( $output, $status ) = _run(
		'status',
		fixtures => {
			'servers.json' => '[]',
			%versioning_ok,
			'versioning-stx-checkpoints.xml' =>
			    "<VersioningConfiguration><Status>Suspended</Status></VersioningConfiguration>\n200",
		},
	);
	is( $status, 0, 'exit 0' );
};

subtest 'a failed versioning read fails the status' => sub {

	# An error body must not pass as "off", per the shared
	# verification rules.
	my ( $output, $status ) = _run(
		'status',
		fixtures => {
			'servers.json' => '[]',
			%versioning_ok,
			'versioning-stx-checkpoints.xml' =>
			    "<Error><Code>AccessDenied</Code></Error>\n403",
		},
	);
	isnt( $status, 0, 'exit non-zero' );
	like( $output, qr/versioning read of stx-checkpoints failed/,
		'the reason' );
};

subtest 'the watchdog reports, and never destroys, an unmanaged server' =>
    sub {
	my ( $output, $status, $calls ) = _run(
		'watchdog',
		fixtures => { 'servers.json' => _server( 60, () ) },
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/watchdog: report: .*no stx:managed tag/,
		'the report' );
	unlike( $calls, qr/tofu.*destroy/, 'no destroy runs' );
    };

subtest 'the watchdog never touches a persistent resource' => sub {
	my ( $output, $status, $calls ) = _run(
		'watchdog',
		fixtures => {
			'servers.json' => _server(
				60 * 24 * 30,
				'stx:managed'   => 'true',
				'stx:lifecycle' => 'persistent',
			),
		},
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/watchdog: skip: .*persistent/, 'the skip' );
	unlike( $calls, qr/tofu.*destroy/, 'no destroy runs' );
};

subtest 'a fresh heartbeat keeps the train stack' => sub {
	my ( $output, $status, $calls ) = _run(
		'watchdog',
		fixtures => {
			'servers.json' => _server(
				60, %train_tags,
				'stx:expires' => _rfc3339( time + 7200 ),
			),
			'heartbeat.txt' => "HTTP/2 200\r\nlast-modified: "
			    . _http_date( time - 300 ) . "\r\n\r\n",
		},
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/watchdog: keep: .*heartbeat is fresh/, 'the keep' );
	unlike( $calls, qr/tofu.*destroy/, 'no destroy runs' );
};

subtest 'an absent heartbeat destroys an idle train stack' => sub {
	my ( $output, $status, $calls ) = _run(
		'watchdog',
		fixtures => {
			'servers.json' => _server(
				60, %train_tags,
				'stx:expires' => _rfc3339( time + 7200 ),
			),
			'heartbeat.txt' => "HTTP/2 404\r\n\r\n",
		},
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/watchdog: destroy: .*heartbeat object is absent/,
		'the destroy verdict' );
	like( $calls,  qr/tofu.*destroy/, 'the destroy runs' );
	like( $output, qr/the destroy is confirmed/, 'the removal read' );
};

subtest 'a passed expiry destroys the train stack' => sub {
	my ( $output, $status, $calls ) = _run(
		'watchdog',
		fixtures => {
			'servers.json' => _server(
				60, %train_tags,
				'stx:expires' => _rfc3339( time - 3600 ),
			),
			'heartbeat.txt' => "HTTP/2 200\r\nlast-modified: "
			    . _http_date( time - 60 ) . "\r\n\r\n",
		},
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/watchdog: destroy: .*passes stx:expires/,
		'the verdict' );
	like( $calls, qr/tofu.*destroy/, 'the destroy runs' );
};

subtest 'a train server without an expiry is a report, not a destroy' => sub {
	my ( $output, $status, $calls ) = _run(
		'watchdog',
		fixtures => { 'servers.json' => _server( 60, %train_tags ) },
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/watchdog: report: .*no stx:expires tag/,
		'the report' );
	unlike( $calls, qr/tofu.*destroy/, 'no destroy runs' );
};

subtest 'a failed heartbeat read is a report, not a destroy' => sub {
	my ( $output, $status, $calls ) = _run(
		'watchdog',
		fixtures => {
			'servers.json' => _server(
				60, %train_tags,
				'stx:expires' => _rfc3339( time + 7200 ),
			),
			'heartbeat.txt' => "HTTP/2 500\r\n\r\n",
		},
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/watchdog: report: .*heartbeat read failed/,
		'the report' );
	unlike( $calls, qr/tofu.*destroy/, 'no destroy runs' );
};

subtest 'a young train stack is not idle yet' => sub {
	my ( $output, $status, $calls ) = _run(
		'watchdog',
		fixtures => {
			'servers.json' => _server(
				10, %train_tags,
				'stx:expires' => _rfc3339( time + 7200 ),
			),
			'heartbeat.txt' => "HTTP/2 404\r\n\r\n",
		},
	);
	is( $status, 0, 'exit 0' );
	like( $output, qr/watchdog: keep: .*younger/, 'the keep' );
	unlike( $calls, qr/tofu.*destroy/, 'no destroy runs' );
};

done_testing();
