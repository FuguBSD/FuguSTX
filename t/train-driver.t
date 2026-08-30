#!/usr/bin/env perl
# ex:ts=8 sw=4:
# Guards for the training driver: the claim and the heartbeat, per
# plan. A stub curl on the PATH stands in place of Object Storage.

use v5.36;
use Test::More;
use File::Temp qw(tempdir);
use FindBin    qw($RealBin);

my $root = "$RealBin/..";
my $dir  = tempdir( CLEANUP => 1 );
my $stub = "$dir/bin";
mkdir $stub or die $!;

# The curl stub logs its argument list, and it answers with the HTTP
# code of STX_STUB_HTTP_CODE. STX_STUB_HEALTH_FAIL fails a health
# probe, for the teach-serve timeout path.
open my $fh, '>', "$stub/curl" or die $!;
print $fh <<'STUB';
#!/usr/bin/env perl
use v5.36;
open my $log, '>>', $ENV{STX_STUB_LOG} or die $!;
say $log join "\x{1}", @ARGV;
close $log;
exit 22 if $ENV{STX_STUB_HEALTH_FAIL} && grep { m{/health} } @ARGV;
print $ENV{STX_STUB_HTTP_CODE} // 200;
STUB
close $fh;
chmod 0755, "$stub/curl";

# The docker stub logs its argument list. STX_STUB_DOCKER_FAIL fails
# a `docker run`, for the failed-start path.
open my $docker, '>', "$stub/docker" or die $!;
print $docker <<'STUB';
#!/usr/bin/env perl
use v5.36;
open my $log, '>>', $ENV{STX_STUB_LOG} or die $!;
say $log "docker @ARGV";
close $log;
exit 1 if $ENV{STX_STUB_DOCKER_FAIL} && $ARGV[0] eq 'run';
STUB
close $docker;
chmod 0755, "$stub/docker";

open my $env, '>', "$dir/train.env" or die $!;
print $env <<'ENV';
SCW_ACCESS_KEY=SCWFAKE
SCW_SECRET_KEY=fake-secret
STX_RUN_ID=run-1
ENV
close $env;

# _driver($command, %options):
#	Run one driver command against the stubs. Return the output,
#	the exit status, and the curl call log.
sub _driver ( $command, %options )
{
	my $log = "$dir/calls-$options{name}.log";
	open my $init, '>', $log or die $!;
	close $init;

	local $ENV{PATH}                   = "$stub:$ENV{PATH}";
	local $ENV{STX_STUB_LOG}           = $log;
	local $ENV{STX_STUB_HTTP_CODE}     = $options{http_code} // 200;
	local $ENV{STX_TRAIN_ENV}          = "$dir/train.env";
	local $ENV{STX_CLAIM_MARKER}       = $options{marker};
	local $ENV{STX_HEARTBEAT_PID}      = $options{pid}
	    // "$dir/heartbeat-$options{name}.pid";
	local $ENV{STX_HEARTBEAT_INTERVAL} = 0.1;

	my $output = qx{$^X $root/scripts/train-driver $command 2>&1};
	my $status = $? >> 8;
	open my $calls, '<', $log or die $!;
	my @lines = <$calls>;
	close $calls;

	return ( $output, $status, \@lines );
}

subtest 'the claim is one conditional write' => sub {
	my $marker = "$dir/claim-marker";
	my ( $output, $status, $calls ) =
	    _driver( 'claim', name => 'claim', marker => $marker );
	is( $status, 0, 'exit 0' );
	is( scalar @$calls, 1, 'one curl call' );
	like( $calls->[0], qr/If-None-Match: \*/, 'the conditional header' );
	like(
		$calls->[0],
		qr{https://stx-checkpoints\.s3\.fr-par\.scw\.cloud/runs/claim$},
		'the claim key is fixed, so two campaigns contend on it'
	);
	ok( -f $marker, 'the local marker exists' );

	# The claim happens once: a second call writes nothing.
	( $output, $status, $calls ) =
	    _driver( 'claim', name => 'claim-again', marker => $marker );
	is( $status, 0, 'a repeated claim of the same run passes' );
	is( scalar @$calls, 0, 'no second conditional write' );
};

subtest 'a lost claim race fails the driver' => sub {
	my ( $output, $status ) = _driver(
		'claim',
		name      => 'claim-race',
		marker    => "$dir/race-marker",
		http_code => 412,
	);
	isnt( $status, 0, 'exit non-zero' );
	like( $output, qr/claimed already/, 'the reason' );
	ok( !-f "$dir/race-marker", 'no marker on a lost race' );
};

subtest 'the heartbeat writes the run key' => sub {
	my ( $output, $status, $calls ) = _driver(
		'heartbeat once',
		name   => 'heartbeat',
		marker => "$dir/hb-marker",
	);
	is( $status, 0, 'exit 0' );
	like(
		$calls->[0],
		qr{runs/run-1/heartbeat},
		'the heartbeat key carries the run identifier'
	);
	like( $calls->[0], qr/\x{1}PUT\x{1}/, 'a PUT write' );
};

subtest 'a checkpoint key carries the run identifier and the step' => sub {

	# COR-BUCKETS-3. A stub aws logs the sync call of each
	# checkpoint directory.
	open my $aws, '>', "$stub/aws" or die $!;
	print $aws <<'AWS';
#!/usr/bin/env perl
use v5.36;
open my $log, '>>', $ENV{STX_STUB_LOG} or die $!;
say $log "aws @ARGV";
close $log;
AWS
	close $aws;
	chmod 0755, "$stub/aws";

	my $outputs = "$dir/outputs/sft-base";
	system( 'mkdir', '-p', "$outputs/checkpoint-100",
		"$outputs/checkpoint-200" ) == 0
	    or die $!;
	open my $config, '>', "$dir/sync.yml" or die $!;
	print $config "output_dir: $outputs\n";
	close $config;

	my ( $output, $status, $calls ) = _driver(
		"sync-checkpoints --config $dir/sync.yml",
		name => 'sync',
	);
	is( $status, 0, 'exit 0' );
	my @syncs = grep { /^aws / } @$calls;
	is( scalar @syncs, 2, 'one sync per checkpoint' );
	like(
		$syncs[0],
		qr{s3://stx-checkpoints/runs/run-1/sft-base/checkpoint-100},
		'the key holds the run identifier and the step number'
	);
};

subtest 'the heartbeat writer repeats on its interval' => sub {
	my $log = "$dir/calls-loop.log";
	open my $init, '>', $log or die $!;
	close $init;

	local $ENV{PATH}                   = "$stub:$ENV{PATH}";
	local $ENV{STX_STUB_LOG}           = $log;
	local $ENV{STX_STUB_HTTP_CODE}     = 200;
	local $ENV{STX_TRAIN_ENV}          = "$dir/train.env";
	local $ENV{STX_HEARTBEAT_PID}      = "$dir/heartbeat-loop.pid";
	local $ENV{STX_HEARTBEAT_INTERVAL} = 0.1;

	my $output = qx{$^X $root/scripts/train-driver heartbeat start};
	is( $? >> 8, 0, 'start exits 0' );
	ok( -f "$dir/heartbeat-loop.pid", 'the pid file exists' );
	select( undef, undef, undef, 0.6 );

	$output = qx{$^X $root/scripts/train-driver heartbeat stop};
	is( $? >> 8, 0, 'stop exits 0' );
	ok( !-f "$dir/heartbeat-loop.pid", 'the pid file is gone' );

	open my $calls, '<', $log or die $!;
	my @lines = <$calls>;
	close $calls;
	cmp_ok( scalar @lines, '>=', 2, 'at least two heartbeat writes' );
};

subtest 'teach-serve claims, serves on localhost, and beats' => sub {
	my $pid = "$dir/heartbeat-teach.pid";
	my ( $output, $status, $calls ) = _driver(
		'teach-serve',
		name   => 'teach-serve',
		marker => "$dir/teach-marker",
		pid    => $pid,
	);
	is( $status, 0, 'exit 0' ) or diag $output;
	ok( -f "$dir/teach-marker", 'the stack is claimed' );
	my ($run) = grep { /^docker run/ } @$calls;
	like( $run, qr/--name stx-vllm/,          'the teacher container' );
	like( $run, qr/-p 127\.0\.0\.1:8000:8000/, 'bound to localhost' );
	like( $run, qr{vllm/vllm-openai:},         'the pinned vLLM image' );
	like( $run, qr/Qwen3-32B-FP8/,             'the pinned checkpoint' );
	ok( -f $pid, 'the heartbeat runs until teach-stop' );

	( $output, $status, $calls ) = _driver(
		'teach-stop',
		name   => 'teach-stop',
		marker => "$dir/teach-marker",
		pid    => $pid,
	);
	is( $status, 0, 'teach-stop exits 0' ) or diag $output;
	ok( ( grep { /^docker rm -f stx-vllm/ } @$calls ),
		'the container is gone' );
	ok( !-f $pid, 'the heartbeat stops' );
};

subtest 'a failed teacher start does not hold the stack' => sub {
	local $ENV{STX_STUB_DOCKER_FAIL} = 1;
	my $pid = "$dir/heartbeat-nostart.pid";
	my ( $output, $status ) = _driver(
		'teach-serve',
		name   => 'teach-nostart',
		marker => "$dir/nostart-marker",
		pid    => $pid,
	);
	isnt( $status, 0, 'exit non-zero' );
	like( $output, qr/failed to start/, 'the reason' );
	ok( !-f $pid, 'the heartbeat stops, so the watchdog can reap' );
};

subtest 'a dead teacher does not hold the stack' => sub {
	local $ENV{STX_TEACH_SERVE_TRIES} = 1;
	local $ENV{STX_STUB_HEALTH_FAIL}  = 1;
	my $pid = "$dir/heartbeat-dead.pid";
	my ( $output, $status, $calls ) = _driver(
		'teach-serve',
		name   => 'teach-dead',
		marker => "$dir/dead-marker",
		pid    => $pid,
	);
	isnt( $status, 0, 'exit non-zero' );
	like( $output, qr/did not answer/, 'the reason' );
	ok( !-f $pid, 'the heartbeat stops, so the watchdog can reap' );
	my @removes = grep { /^docker rm -f stx-vllm/ } @$calls;
	cmp_ok( scalar @removes, '>=', 2, 'the container is swept' );
};

done_testing();
