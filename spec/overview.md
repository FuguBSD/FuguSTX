# Overview

## Product

**G1 — the product.** FuguSTX turns raw English text into offset-faithful
linguistic annotations. The annotations are tokens, sentences, universal POS
tags, lemmas, morphological features, and dependency relations. A linter
consumes the annotations and stays a rulebook.

## The pilot

The product goal of FuguSTX stands. The build rehearses the FuguTTX production
pipeline at small scale, on the same components, at real prices. Cheap learnings
are a deliverable. A marker of the form "Rehearses: FuguTTX IAC-TRAIN" ties a
component to the FuguTTX unit that it rehearses.

**G2 — the pilot.** FuguSTX rehearses the FuguTTX pipeline before FuguTTX pays
full price. Where a FuguTTX component fits, FuguSTX must use that component.
This rule holds even where a lighter tool serves G1 alone.

**The rank rule.** G1 defines the interfaces. G2 defines the implementation.
When the two conflict, a decision in [DECISIONS.md](DECISIONS.md) records the
choice.

## Deliverables

The deliverables are the model, the `stx` engine, the `stx-ste` reference
client, and [the learning](LEARNING.md).

## Accepted costs

The design trades a small deployment for pilot value. The table names each
accepted cost.

| Accepted cost                                   | Reason                                               |
| ----------------------------------------------- | ---------------------------------------------------- |
| The model file is near 0.6 GB                   | The engine is a Qwen3-0.6B fine-tune in GGUF form    |
| Cold start takes seconds                        | llama.cpp loads a quantized model at start           |
| Inference is slower than a purpose-built tagger | The runtime mirrors FuguTTX D2                       |
| Training needs a cloud GPU                      | The training pipeline mirrors FuguTTX D3, on purpose |

Two guarantees survive the trade: the annotation contract, and the byte-offset
guarantee. [T10](DECISIONS.md#t10) keeps the door open for a small purpose-built
engine behind the same interface.

## The name

STX carries three true meanings, and each one fits the project.

- **Saxitoxin.** STX is the other pufferfish toxin. Saxitoxin and tetrodotoxin
  block the same sodium channel. FuguSTX is the smaller relative of FuguTTX,
  with the same mechanism.
- **Syntax.** The letters S, T, and X are the skeleton of the word "syntax".
  Syntax is the product.
- **Start of text.** STX is ASCII 0x02, the start-of-text control character. The
  pilot comes before the main text.

A fugu chef earns the license on a supervised preparation before the chef serves
guests. FuguSTX is that preparation: the same knives, the same procedure, and a
smaller fish. The name is still a scope statement.
