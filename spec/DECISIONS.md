# Decisions

These decisions control all plans. A plan must not go against a decision. To
change a decision, change this document first.

<a id="t1"></a>

## T1 — Base model: Qwen3-0.6B (Apache 2.0)

Mirrors FuguTTX D1: the same model family, the same tokenizer, and the same
license. The model is small, so a full training run costs single-digit euros.

<a id="t2"></a>

## T2 — Inference: llama.cpp, CPU only, greedy decoding

Mirrors FuguTTX D2. The artifact is one GGUF file at Q8_0. Determinism holds
under three pins: the llama.cpp version, the thread count, and the model hash.
Every output record carries the model hash. Details: [engine](engine.md).

<a id="t3"></a>

## T3 — Training: Axolotl on a Scaleway H100, fully as code

Mirrors FuguTTX D3 in the stack and the execution. The precision and the adapter
follow the model size. A model that fits the GPU in bf16 with its optimizer
states trains in bf16, as a full fine-tune or as a bf16 adapter. A 4-bit load is
the memory escape for a model that does not fit. The H100 is larger than a 0.6B
run needs, and that is the point. The pilot exercises the H100 quota, the live
price, and the train stack at low stakes. The L40S stays as the budget escape.
Details: [training](training.md), [infrastructure](infrastructure.md).

<a id="t4"></a>

## T4 — Method: one CPT rehearsal pass, then SFT

Mirrors the shape of FuguTTX D4, at near 1/1000 of the scale. The CPT pass
exists to rehearse `make train-cpt`. A seeded, paired comparison against the
noise floor decides whether the pass moves the scores. If the pass does not move
the scores, the product drops it, and LEARNING records why. Details:
[training](training.md).

<a id="t5"></a>

## T5 — Generators: two model families write the mirrors, a cross-family labeler aligns, and a judge admits each pair

Qwen3-32B under vLLM on the train instance stays the FuguTTX teacher, served the
same way, and it is one generator. A second generator of a different model
family writes a share of the mirrors through a headless client session under a
dedicated profile. No split then carries the signature of one family. A labeler
of a different model family than the generator of the pair proposes the
alignment label of each segment. Two seeded passes must agree, and the judge
checks each label mechanically. The judge admits a pair only when four checks
pass. The generator has not memorized the human document, the mirror holds no
sentence of the original, the structure matches, and the labels pass. This
mirrors the FuguTTX rule that a teacher output enters training only through a
filter. Details: [training](training.md).

<a id="t6"></a>

## T6 — Corpus lanes: two lanes, and the lane rule is absolute

The training lane holds redistributable pairs. The eval lane holds held-out
pairs, plus a human set from a later era than every training document. Eval data
must never enter training. Contamination drives the rule here. Author copyright
drives it in FuguTTX D6. The mechanics are identical, so the rehearsal is
faithful. Details: [corpus](corpus.md).

<a id="t7"></a>

## T7 — Harness: Perl 5 over Fugu

Base modules, plus the module allow-list of FuguTTX D7. The harness is the only
writer of offsets, and the only caller of llama.cpp. Details:
[engine](engine.md).

<a id="t8"></a>

## T8 — Evaluation runs in real OpenBSD guests

The artifact suite runs inside OpenBSD guests under FuguVM, on the Scaleway dev
host. The suite uses parallel guests, snapshot restores between runs, and scores
read from guest output. These are the mechanics of the FuguTTX agentic suite,
minus the agent. Details: [evaluation](evaluation.md).

<a id="t9"></a>

## T9 — Infrastructure: the shared infrastructure instructions, applied

Same stacks, same layout, same state rules, same credential split, and the same
watchdog, from the `infra` pack of FuguBSD/Tooling. The tag prefix is `stx:`.
The project gets its own Scaleway Project in the same Organization. The budget
is EUR 300 per month. Details: [infrastructure](infrastructure.md).

<a id="t10"></a>

## T10 — The finding contract is engine-independent

The output format must not expose the language model. A future purpose-built
engine can replace the model without a client change. This escape hatch is a
requirement, not a hope. Details: [engine](engine.md).

<a id="t11"></a>

## T11 — The learning is a deliverable, in two records

The learning of G2 lives in two records, and each one has one job.

The library is the working record. It is the shared repository FuguBSD/Wiki, and
it holds every observation and every admitted claim of every campaign. An
observation reaches a commit there at capture time, so a crash loses nothing.

This ledger is the delivered record. It receives one batch for each campaign, at
the closing pull request. A batch cites the library pages that hold its
evidence, and it holds no per-entry prose.

A learning that contradicts the FuguTTX specification must become a FuguTTX
specification change, not a note. Details: [learning](LEARNING.md).

<a id="t12"></a>

## T12 — Method: the model learns from contrastive pairs, not from a grammar

The goal is the tells of machine-written prose in English technical text. The
engine reports one finding per segment, and an agent repairs the text from the
findings. The model learns from aligned pairs: a human document, and a mirror of
the same facts. A generator writes the mirror without sight of the human prose.
A grammar analyzer with a rulebook loses on three counts. It sees only what the
grammar exposes, and the measured tells are content-shaped. Every grammar rule
also fires on human text, so its precision as a detector is poor. A rulebook
chases each model generation by hand, and a pair corpus regenerates. The
measured basis is a probe of 2026-09-24 with Claude Opus on OpenBSD 3.0 manual
pages. A famous page sits in the training set of the generator: strlcpy.3
returns at recall ratio 0.99, and photurisd.8, deleted early, at 0.12. A mirror
written from a structure skeleton plus the source code rebuilds a memorized
page, cat.1 at 0.93. Surface lexical markers do not separate a human page from
its mirror; the differences are completeness, rationale sentences, and invented
facts. The regex `ste-lint` of the org pack stays the style gate of every
FuguBSD repository, and FuguSTX builds no style checker. The tell inventory is a
versioned registry, and the grammar is a generated copy. Lexical tells decay
within a model generation, and the syntactic and content tells persist. The
inventory must extend and retire without a schema change. Details:
[corpus](corpus.md), [engine](engine.md).

<a id="t13"></a>

## T13 — The pilot gate: a zero-training baseline first, and one bar

Before the first SFT pass on a pair corpus, a zero-training baseline scores the
base model on the same pairs, as a perplexity contrast. The SFT pass is a
refinement of that baseline. The operator sets the pilot bar after the baseline
run, and the evaluation document holds it. The pilot commits to the method when
the tier T1 sweep clears the bar. Below the bar, the operator decides, and
LEARNING records why. Details: [evaluation](evaluation.md).
