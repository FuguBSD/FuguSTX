#!/usr/bin/env perl
# ex:ts=8 sw=4:
# Guards for the promote and teach verbs of scripts/train. A stub
# tool set on the PATH stands in place of Object Storage, OpenTofu,
# SSH, and uv: each stub logs its call, and it materializes each
# file that the verb reads next.

use v5.36;
use Test::More;
use Digest::SHA qw(sha256_hex);
use File::Temp  qw(tempdir);
use FindBin     qw($RealBin);

my $root = "$RealBin/..";
my $dir  = tempdir( CLEANUP => 1 );
my $stub = "$dir/bin";
mkdir $stub or die $!;

open my $fh, '>', "$stub/aws" or die $!;
print $fh <<'STUB';
#!/usr/bin/env perl
use v5.36;
open my $log, '>>', $ENV{STX_STUB_LOG} or die $!;
say $log "aws @ARGV";
close $log;
my ( $src, $dst ) = @ARGV[ 4, 5 ];
exit 0 if $dst =~ m{^s3://};
open my $out, '>', $dst or die $!;
print $out $src =~ /scorecard/ ? $ENV{STX_STUB_CARD} : $ENV{STX_STUB_GGUF};
close $out;
STUB
close $fh;
chmod 0755, "$stub/aws";

my $gguf = "fake-gguf-bytes\n";
my $hash = sha256_hex($gguf);

# _train($argv, %options):
#	Run one train call against the stub. Return the output, the
#	exit status, and the aws call log.
sub _train ( $argv, %options )
{
	my $log = "$dir/calls-$options{name}.log";
	open my $init, '>', $log or die $!;
	close $init;

	local $ENV{PATH}         = "$stub:$ENV{PATH}";
	local $ENV{STX_STUB_LOG} = $log;
	local $ENV{STX_STUB_GGUF} = $gguf;
	local $ENV{STX_STUB_CARD} =
	    $options{card} // qq({\n  "model_hash": "$hash"\n}\n);

	my $output = qx{$^X $root/scripts/train $argv 2>&1};
	my $status = $? >> 8;
	open my $calls, '<', $log or die $!;
	my @lines = <$calls>;
	close $calls;

	return ( $output, $status, \@lines );
}

subtest 'the promote copies and verifies' => sub {
	my ( $output, $status, $calls ) = _train(
		'promote --name sft-cpt --run-id run-1',
		name => 'happy',
	);
	is( $status, 0, 'exit 0' );
	is( scalar @$calls, 3, 'three S3 calls' );
	like(
		$calls->[0],
		qr{cp s3://stx-checkpoints/runs/run-1/gguf/sft-cpt\.gguf },
		'the GGUF comes from the checkpoint bucket'
	);
	like(
		$calls->[1],
		qr{cp s3://stx-artifacts/runs/run-1/scorecard-dev-sft-cpt\.json },
		'the dev scorecard gates the copy'
	);
	like(
		$calls->[2],
		qr{ s3://stx-artifacts/runs/run-1/stx-sft-cpt\.gguf$},
		'the artifact lands under the run prefix'
	);
	like( $output, qr/sha256 \Q$hash\E/, 'the sha256 print' );
};

subtest 'a hash mismatch stops the promote' => sub {
	my ( $output, $status, $calls ) = _train(
		'promote --name sft-cpt --run-id run-1',
		name => 'mismatch',
		card => qq({\n  "model_hash": "@{[ '0' x 64 ]}"\n}\n),
	);
	isnt( $status, 0, 'exit non-zero' );
	like( $output, qr/does not match/, 'the reason' );
	is( scalar @$calls, 2, 'no upload after the mismatch' );
};

# The remote-verb stubs. tofu prints the instance address, ssh logs
# its argument list, aws materializes each download, and uv writes
# each file its flags name.
my $remote = "$dir/remote-bin";
mkdir $remote or die $!;

sub _stub ( $name, $body )
{
	open my $handle, '>', "$remote/$name" or die $!;
	print $handle "#!/usr/bin/env perl\nuse v5.36;\n";
	print $handle <<'COMMON';
open my $log, '>>', $ENV{STX_STUB_LOG} or die $!;
say $log join ' ', $0 =~ s{.*/}{}r, @ARGV;
close $log;
COMMON
	print $handle $body;
	close $handle;
	chmod 0755, "$remote/$name";

	return;
}

_stub( 'tofu', <<'STUB' );
if ( grep { $_ eq 'output' } @ARGV ) { print "198.51.100.7\n"; }
exit 0;
STUB

_stub( 'ssh', <<'STUB' );
unless ( -t STDIN ) { local $/; my $drain = <STDIN>; }
exit 0;
STUB

_stub( 'aws', <<'STUB' );
my ($cp) = grep { $ARGV[$_] eq 'cp' } 0 .. $#ARGV;
exit 0 unless defined $cp;
my ( $src, $dst ) = @ARGV[ $cp + 1, $cp + 2 ];
exit 0 if $dst =~ m{^s3://};
use File::Path qw(make_path);
if ( grep { $_ eq '--recursive' } @ARGV ) {
	make_path($dst);
	open my $a, '>', "$dst/accepted-a.jsonl" or die $!;
	print $a qq({"sent_id":"a1","text":"A shared sentence."}\n);
	print $a qq({"sent_id":"a2","text":"One unique sentence."}\n);
	close $a;
	open my $b, '>', "$dst/accepted-b.jsonl" or die $!;
	print $b qq({"sent_id":"b1","text":"A shared sentence."}\n);
	close $b;
	exit 0;
}
$dst =~ m{^(.*)/} and make_path($1);
open my $out, '>', $dst or die $!;
print $out "{}\n";
close $out;
STUB

_stub( 'uv', <<'STUB' );
use File::Path qw(make_path);
for my $flag (qw(--out --output --accepted --rejects --report)) {
	my ($at) = grep { $ARGV[$_] eq $flag } 0 .. $#ARGV;
	next unless defined $at;
	my $path = $ARGV[ $at + 1 ];
	$path =~ m{^(.*)/} and make_path($1);
	open my $out, '>', $path or die $!;
	print $out "{}\n";
	close $out;
}
STUB

# _remote_train($argv):
#	Run one train call against the remote-verb stub set. Return
#	the output, the exit status, and the stub call log.
sub _remote_train ($argv)
{
	my $log = "$dir/remote-calls-" . ( $argv =~ s/\W+/-/gr ) . '.log';
	open my $init, '>', $log or die $!;
	close $init;

	local $ENV{PATH}         = "$remote:$ENV{PATH}";
	local $ENV{STX_STUB_LOG} = $log;
	delete local $ENV{GITHUB_RUN_ID};

	my $output = qx{$^X $root/scripts/train $argv 2>&1};
	my $status = $? >> 8;
	open my $calls, '<', $log or die $!;
	my @lines = <$calls>;
	close $calls;

	return ( $output, $status, \@lines );
}

subtest 'the sft-aug verb drives the driver configuration' => sub {
	my ( $output, $status, $calls ) =
	    _remote_train('sft-aug');
	is( $status, 0, 'exit 0' ) or diag $output;
	ok( ( grep { /^ssh .*train\/sft-aug\.yml/ } @$calls ),
		'the remote run takes train/sft-aug.yml' );
};

subtest 'the teach-serve verb dispatches the driver step' => sub {
	my ( $output, $status, $calls ) = _remote_train('teach-serve');
	is( $status, 0, 'exit 0' ) or diag $output;
	ok( ( grep { /^ssh .*train-driver teach-serve/ } @$calls ),
		'the driver serves the teacher' );
	( $output, $status, $calls ) = _remote_train('teach-stop');
	is( $status, 0, 'teach-stop exits 0' ) or diag $output;
	ok( ( grep { /^ssh .*train-driver teach-stop/ } @$calls ),
		'the driver stops the teacher' );
};

subtest 'the teach verb tunnels, filters, and uploads' => sub {
	my $run = "run-t$$";
	my ( $output, $status, $calls ) =
	    _remote_train("teach --run-id $run --batch b1 --count 5");
	is( $status, 0, 'exit 0' ) or diag $output;

	ok( ( grep { /^ssh .*claim && scripts\/train-driver heartbeat start/ }
			@$calls ),
		'the verb claims the stack and beats the heartbeat' );
	my ($tunnel) = grep { /^ssh .*-L 8000:127\.0\.0\.1:8000/ } @$calls;
	ok( $tunnel, 'the tunnel forwards the localhost endpoint' );
	like( $tunnel, qr/ServerAliveInterval=30/, 'with keepalives' );
	ok( ( grep { /^ssh .*-O exit/ } @$calls ), 'the tunnel closes' );

	ok( ( grep { /^uv .*stx_corpus\.teacher .*--count 5/ } @$calls ),
		'the client runs one bounded batch' );
	ok( ( grep { /^uv .*stx_corpus\.judge/ } @$calls ),
		'the filter disposes' );
	ok( ( grep { /^uv .*stx_corpus\.pairs .*--augmentation/ } @$calls ),
		'the pairs rebuild reads the accepted records' );

	ok( ( grep { m{ s3://stx-corpus/runs/\Q$run\E/accepted-b1\.jsonl$} }
			@$calls ),
		'the accepted records land under the run prefix' );
	ok( ( grep {
			m{ s3://stx-artifacts/runs/\Q$run\E/teach-rejects-b1\.jsonl$}
		} @$calls ),
		'the reject log goes to the artifacts bucket' );
	ok( ( grep {
			m{ s3://stx-artifacts/runs/\Q$run\E/teach-report-b1\.json$}
		} @$calls ),
		'the rate report goes to the artifacts bucket' );
	ok( ( grep { m{ s3://stx-corpus/pairs-aug\.jsonl$} } @$calls ),
		'the augmented pairs reach the corpus bucket' );

	# COR-AUG-1: a rejected record must not reach the corpus bucket.
	my @corpus_uploads =
	    grep { m{^aws .* s3://stx-corpus/} } @$calls;
	ok( !( grep { /rejects|report/ } @corpus_uploads ),
		'no reject reaches the corpus bucket' );

	# A sentence that two batches both propose enters the pairs
	# once.
	my $all = "$root/explore/teach/$run-b1/accepted-all.jsonl";
	open my $rebuilt, '<', $all or die "read $all: $!";
	my @lines = <$rebuilt>;
	close $rebuilt;
	is( scalar @lines, 2, 'the cross-batch duplicate is dropped' );
};

subtest 'the teach option guards hold' => sub {
	my ( $output, $status, $calls ) = _remote_train('teach --batch b1');
	isnt( $status, 0, 'teach needs --run-id' );
	is( scalar @$calls, 0, 'no tool call without a run' );

	( $output, $status, $calls ) = _remote_train('cpt --batch b1');
	isnt( $status, 0, 'only teach takes --batch' );
	is( scalar @$calls, 0, 'no tool call either' );

	( $output, $status, $calls ) =
	    _remote_train(q{teach --run-id 'run 1' --batch b1});
	isnt( $status, 0, 'a run name must stay one word' );
	is( scalar @$calls, 0, 'no tool call with a bad name' );
};

subtest 'the option guards hold' => sub {
	my ( $output, $status, $calls ) = _train(
		'promote --run-id run-1',
		name => 'no-name',
	);
	isnt( $status, 0, 'promote needs --name' );
	is( scalar @$calls, 0, 'no S3 call' );

	( $output, $status, $calls ) = _train(
		'promote --name sft-cpt',
		name => 'no-run-id',
	);
	isnt( $status, 0, 'promote needs --run-id' );
	is( scalar @$calls, 0, 'no S3 call without a run' );

	( $output, $status, $calls ) = _train(
		'gguf --name sft-cpt --run-id run-1',
		name => 'wrong-verb',
	);
	isnt( $status, 0, 'only promote takes --run-id' );
	is( scalar @$calls, 0, 'no S3 call either' );
};

done_testing();
