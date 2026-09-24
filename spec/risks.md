# Risks

This document names the risks of the pilot, and it names the mitigation of each
risk. The units are citation-only: a plan or a LEARNING entry can cite a risk,
and no code implements one.

<a id="rsk-acc"></a>

## Accuracy

A 0.6B classifier can miss the tells of a strong generator. The
[tier T1 gates](evaluation.md#evl-tiers) decide, not hope. Decision
[T10](DECISIONS.md#t10) keeps the escape hatch open.

<a id="rsk-confound"></a>

## Confounds

Every pair contrasts one era and one register against one generator, so the
model can learn era, register, or generator identity. COR-PAIRS-6, COR-PAIRS-7,
and the later-era human set of COR-LANES-3 mitigate.

<a id="rsk-determ"></a>

## Determinism

llama.cpp output can vary with thread count and version. The pins of decision
[T2](DECISIONS.md#t2) are requirements, and a violation fails
[the artifact suite](evaluation.md#evl-suite).

<a id="rsk-drift"></a>

## Generator drift

A new model generation carries different tells. The mitigation is decision
[T12](DECISIONS.md#t12): regenerate the mirrors, and run one SFT pass.

<a id="rsk-mem"></a>

## Memorization

A human document in the training set of the generator gives a pair with human
text on both sides. That pair is label noise. The memorization check of
[the judge filter](training.md#trn-teach) and COR-PAIRS-3 mitigate.

<a id="rsk-findings"></a>

## Misleading findings

The pilot can produce false confidence about 4B-scale behavior.
[LRN-SCOPE](LEARNING.md#lrn-scope) bounds every claim.

<a id="rsk-scope"></a>

## Scope leak

G2 pulls the project toward FuguTTX features. The test: FuguSTX builds nothing
that neither G1 nor a LEARNING row can name.

<a id="rsk-seq"></a>

## Sequencing

The pilot delays FuguTTX by its own duration. The mitigation is scale: the model
is small, so each pass completes in hours.
