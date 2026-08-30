# Decisions

These eleven decisions control all plans. A plan must not go against a decision.
To change a decision, change this document first.

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

## T3 — Training: Axolotl QLoRA on a Scaleway H100, fully as code

Mirrors FuguTTX D3. The H100 is larger than a 0.6B run needs, and that is the
point. The pilot exercises the H100 quota, the live price, and the train stack
at low stakes. The L40S stays as the budget escape. Details:
[training](training.md), [infrastructure](infrastructure.md).

<a id="t4"></a>

## T4 — Method: one CPT rehearsal pass, then SFT

Mirrors the shape of FuguTTX D4, at near 1/1000 of the scale. The CPT pass
exists to rehearse `make train-cpt`. If the pass does not move the scores, the
product drops it, and LEARNING records why. Details: [training](training.md).

<a id="t5"></a>

## T5 — Teacher: Qwen3-32B under vLLM, on the train instance

The same teacher, served the same way, as FuguTTX specifies. The teacher
proposes, and a verifier disposes. This mirrors the FuguTTX rule that a teacher
output enters training only through a filter. Details: [training](training.md).

<a id="t6"></a>

## T6 — Corpus lanes: two lanes, and the lane rule is absolute

The training lane holds redistributable data. The eval lane holds held-out data.
Eval data must never enter training. Contamination drives the rule here. Author
copyright drives it in FuguTTX D6. The mechanics are identical, so the rehearsal
is faithful. Details: [corpus](corpus.md).

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

## T10 — The annotation contract is engine-independent

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
