# The engine

The `stx` engine reads English technical text, and it reports the tells of
machine-written prose, one finding per segment. [overview.md](overview.md)
defines the goals G1 and G2.

<a id="eng-split"></a>

## Division of labor

The engine divides the analysis between the harness and the model. The harness
follows [T7](DECISIONS.md#t7). The model judges each segment. This division
keeps the offset guarantee under a probabilistic model.

Rehearses: the FuguTTX harness patterns.

- **ENG-SPLIT-1** — The harness must segment the text into sentences
  deterministically, in Perl.
- **ENG-SPLIT-2** — The harness must compute every byte offset from its own
  tokenizer.
- **ENG-SPLIT-3** — The model must not produce an offset.
- **ENG-SPLIT-4** — The harness must be the only writer of offsets and the only
  caller of llama.cpp.

<a id="eng-schema"></a>

## The finding schema

The model output has one legal shape: the finding schema. A registry file
defines the tell inventory, and the grammar and the alignment label list are
generated copies of it. This mirrors the FuguTTX rule that tool calls obey the
harness schemas at generation time.

- **ENG-SCHEMA-1** — A llama.cpp GBNF grammar must constrain the model output to
  the finding schema.
- **ENG-SCHEMA-2** — The schema must hold one record per segment: the verdict,
  and a tell category from the registry.
- **ENG-SCHEMA-3** — Each category must map to one repair action of a closed
  set: keep, compress, delete, rewrite, or verify. An agent then acts on a
  finding without a second model call.
- **ENG-SCHEMA-4** — A registry file must be the one definition of the tell
  inventory. The grammar and the alignment label list must be generated copies
  of it. A test must compare each generated copy byte for byte with the
  registry.
- **ENG-SCHEMA-5** — Each registry row must hold the id, the level, the repair
  action, the version since, the version retired, the description, and the
  evidence. The level is lexical, syntactic, structural, or content.
- **ENG-SCHEMA-6** — The inventory must carry a version. A retired category must
  stay in the registry and leave the grammar, and an id must not return.
- **ENG-SCHEMA-7** — `none` must be the only reserved id, and the inventory must
  hold no catch-all category. Each other id names one tell with one repair
  action.

<a id="eng-determ"></a>

## Determinism

The engine is deterministic. The guarantee holds under the pins of
[T2](DECISIONS.md#t2).

- **ENG-DETERM-1** — Every output record must carry the byte offsets from the
  harness tokenizer and the model hash.
- **ENG-DETERM-2** — Same bytes in must give the same findings out, for one
  model hash and one engine version.

<a id="eng-contract"></a>

## The finding contract

Decision [T10](DECISIONS.md#t10) makes the finding contract engine-independent.
This escape hatch is a requirement, not a hope.

- **ENG-CONTRACT-1** — The output format must not expose the language model.
- **ENG-CONTRACT-2** — A future purpose-built engine can replace the model
  without a client change.

<a id="eng-iface"></a>

## Interfaces

Two interfaces expose the engine.

- **ENG-IFACE-1** — `stx analyze` must read text and emit JSON, one finding per
  segment, for shell pipelines and CI.
- **ENG-IFACE-2** — A local daemon over `Fugu::EventLoop` must keep one warm
  engine for editors and polyglot clients.
