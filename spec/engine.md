# The engine

The `stx` engine turns English text into annotations for prose linters. This
document specifies the engine and its reference client `stx-ste`.
[overview.md](overview.md) defines the goals G1 and G2.

<a id="eng-split"></a>

## Division of labor

The engine divides the analysis between the harness and the model. The harness
follows [T7](DECISIONS.md#t7). The model labels the tokens. This division keeps
the offset guarantee under a probabilistic model.

Rehearses: the FuguTTX harness patterns.

- **ENG-SPLIT-1** — The harness must segment and tokenize the text
  deterministically, in Perl.
- **ENG-SPLIT-2** — The harness must compute every byte offset from its own
  tokenizer.
- **ENG-SPLIT-3** — The model must not produce an offset.
- **ENG-SPLIT-4** — The harness must be the only writer of offsets and the only
  caller of llama.cpp.

<a id="eng-schema"></a>

## The annotation schema

The model output has one legal shape: the annotation schema. This mirrors the
FuguTTX rule that tool calls obey the harness schemas at generation time.

- **ENG-SCHEMA-1** — A llama.cpp GBNF grammar must constrain the model output to
  the annotation schema.
- **ENG-SCHEMA-2** — The schema must hold one record per token: UPOS, lemma,
  head, deprel, and feats.

<a id="eng-determ"></a>

## Determinism

The engine is deterministic. The guarantee holds under the pins of
[T2](DECISIONS.md#t2).

- **ENG-DETERM-1** — Every output record must carry the byte offsets from the
  harness tokenizer and the model hash.
- **ENG-DETERM-2** — Same bytes in must give the same annotations out, for one
  model hash and one engine version.

<a id="eng-contract"></a>

## The annotation contract

Decision [T10](DECISIONS.md#t10) makes the annotation contract
engine-independent. This escape hatch is a requirement, not a hope.

- **ENG-CONTRACT-1** — The output format must not expose the language model.
- **ENG-CONTRACT-2** — A future purpose-built engine can replace the model
  without a client change.

<a id="eng-iface"></a>

## Interfaces

Two interfaces expose the engine.

- **ENG-IFACE-1** — `stx analyze` must read text and emit JSON or CoNLL-U, for
  shell pipelines and CI.
- **ENG-IFACE-2** — A local daemon over `Fugu::EventLoop` must keep one warm
  engine for editors and polyglot clients.

<a id="eng-lexicon"></a>

## The lexicon

The lexicon is the controlled-language primitive of the engine.

- **ENG-LEXICON-1** — A lexicon must load at run time: approved words, with the
  allowed parts of speech of each word.
- **ENG-LEXICON-2** — The output must mark the dictionary status of every token.

<a id="eng-ste"></a>

## The reference client

`stx-ste` is an ASD-STE100 checker, and the reference client of the engine.
Every FuguBSD repository runs the regex `ste-lint`. The client targets that job,
so the organization is consumer zero.

- **ENG-STE-1** — `stx-ste` must check sentence-length limits, approved words
  per part of speech, and banned constructions.
- **ENG-STE-2** — The checks for passive voice and noun clusters must be queries
  over the annotations.
