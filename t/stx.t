#!/usr/bin/env perl
# ex:ts=8 sw=4:
# Guards for the thin stx harness command (ENG-SPLIT-3, ENG-SPLIT-4).
#
# A stub stands in place of llama.cpp, per plan. The stub records its
# argument list, so the test can prove that the harness passes the
# committed grammar and greedy decoding to llama.cpp.

use v5.36;
use Test::More;
use File::Temp qw(tempdir);
use FindBin    qw($RealBin);
use JSON::PP   ();

my $root = "$RealBin/..";
my $dir  = tempdir( CLEANUP => 1 );
my $json = JSON::PP->new;

# The stub: it finds the -p prompt, it logs the argument list, and it
# answers per STX_STUB_MODE. The "ok" mode writes one legal record for
# each token line of the prompt.
my $stub = "$dir/llama-stub";
open my $fh, '>', $stub or die "write $stub: $!";
print $fh <<'STUB';
use v5.36;
my %options;
my @argv = @ARGV;
while (@argv) {
	my $flag = shift @argv;
	$options{$flag} = @argv && $argv[0] !~ /^-/ ? shift @argv : 1;
}
open my $log, '>', $ENV{STX_STUB_LOG} or die $!;
print $log join( "\x{1}", @ARGV );
close $log;
exit 3 if ( $ENV{STX_STUB_MODE} // 'ok' ) eq 'fail';
my @lines = grep { length } split /\n/, $options{'-p'};
shift @lines if $ENV{STX_STUB_MODE} eq 'short';
for my $line (@lines) {
	my ( $index, $form ) = split /\t/, $line;
	print "NOUN\t$form\t0\troot\t_\n";
}
print "[end of text]\n";
STUB
close $fh;

# _run($mode, $input):
#	Run `stx label` against the stub, with $input on stdin. Return
#	the standard output, the exit status, and the logged stub
#	argument list.
sub _run ( $mode, $input )
{
	my $infile = "$dir/input.jsonl";
	open my $in, '>', $infile or die $!;
	print $in $input;
	close $in;
	local $ENV{STX_STUB_MODE} = $mode;
	local $ENV{STX_STUB_LOG}  = "$dir/argv.log";
	local $ENV{STX_LLAMA}     = qq{$^X $stub};
	my $out = qx{$^X $root/bin/stx label -m $dir/model.gguf < $infile 2>$dir/err.log};
	my $status = $? >> 8;
	my @argv;

	if ( open my $log, '<', "$dir/argv.log" ) {
		local $/ = undef;
		@argv = split /\x{1}/, <$log>;
		close $log;
	}

	return ( $out, $status, \@argv );
}

my $request = $json->encode( { tokens => [ 'A', 'cat' ] } ) . "\n";

subtest 'a legal output labels each token' => sub {
	my ( $out, $status, $argv ) = _run( 'ok', $request );
	is( $status, 0, 'exit 0' );
	my $reply = $json->decode($out);
	is( scalar @{ $reply->{labels} }, 2, 'one record per token' );
	is( $reply->{labels}[0]{upos},   'NOUN', 'the UPOS field' );
	is( $reply->{labels}[1]{lemma},  'cat',  'the lemma field' );
	is( $reply->{labels}[0]{head},   0,      'the head field is a number' );
	is( $reply->{labels}[0]{deprel}, 'root', 'the deprel field' );
	is( $reply->{labels}[0]{feats},  '_',    'the feats field' );
};

subtest 'the harness passes the grammar and greedy decoding' => sub {
	my ( $out, $status, $argv ) = _run( 'ok', $request );
	my %options;
	my @rest = @$argv;
	while (@rest) {
		my $flag = shift @rest;
		$options{$flag} = @rest ? $rest[0] : 1;
	}
	is( $options{'--grammar-file'}, "$root/share/annotation.gbnf",
		'the committed grammar file' );
	ok( -f $options{'--grammar-file'}, 'the grammar file exists' );
	is( $options{'--temp'}, 0, 'greedy decoding' );
	is( $options{'-p'},     "1\tA\n2\tcat\n\n", 'the input serialization' );
};

subtest 'a record count mismatch is a data error' => sub {
	my ( $out, $status ) = _run( 'short', $request );
	is( $status, 0, 'exit 0: the sweep decides' );
	my $reply = $json->decode($out);
	like( $reply->{error}, qr/1 records for 2 tokens/, 'the reason' );
};

subtest 'a llama.cpp failure fails the harness' => sub {
	my ( $out, $status ) = _run( 'fail', $request );
	isnt( $status, 0, 'a program error exits non-zero' );
};

subtest 'each input line gets one output line' => sub {
	my $two = $request . $json->encode( { tokens => ['Run'] } ) . "\n";
	my ( $out, $status ) = _run( 'ok', $two );
	is( $status, 0, 'exit 0' );
	my @lines = grep { length } split /\n/, $out;
	is( scalar @lines, 2, 'two replies' );
	is( scalar @{ $json->decode( $lines[1] )->{labels} }, 1, 'the second' );
};

subtest 'an input without a tokens list is refused' => sub {
	my ( $out, $status ) = _run( 'ok', qq({"text":"A cat"}\n) );
	isnt( $status, 0, 'exit non-zero' );
};

done_testing();
