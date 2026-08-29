#!/usr/bin/env perl
# ex:ts=8 sw=4:
# Guards for the stackless promote of scripts/train. A stub aws on
# the PATH stands in place of Object Storage: it logs each call, and
# it materializes each download.

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

subtest 'the stackless promote copies and verifies' => sub {
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
