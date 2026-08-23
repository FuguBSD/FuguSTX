# Risks

This document names the risks of the pilot, and it names the mitigation of each
risk. The units are citation-only: a plan or a register entry can cite a risk,
and no code implements one.

<a id="rsk-acc"></a>

## Accuracy

A 0.6B generalist can miss the accuracy of a purpose-built tagger. The
[tier T1 gates](evaluation.md#evl-tiers) decide, not hope. Decision
[T10](DECISIONS.md#t10) keeps the escape hatch open.

<a id="rsk-determ"></a>

## Determinism

llama.cpp output can vary with thread count and version. The pins of decision
[T2](DECISIONS.md#t2) are requirements, and a violation fails
[the artifact suite](evaluation.md#evl-suite).

<a id="rsk-findings"></a>

## Misleading findings

The pilot can produce false confidence about 4B-scale behavior.
[REG-SCOPE](register.md#reg-scope) bounds every claim.

<a id="rsk-scope"></a>

## Scope leak

G2 pulls the project toward FuguTTX features. The test: FuguSTX builds nothing
that neither G1 nor a register row can name.

<a id="rsk-seq"></a>

## Sequencing

The pilot delays FuguTTX by its own duration. The mitigation is scale: the model
is small, so each pass completes in hours.
