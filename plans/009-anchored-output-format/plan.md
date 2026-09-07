# 009 — The anchored output format

Between half a percent and four percent of the sentences fail on record shape,
by model and treebank. Each one scores every token wrong. The grammar cannot
force one record per token. UPOS sits at 0.94 while LAS sits at 0.77, so the
head and the label are the bottleneck. The model emits an absolute head index
with no anchor to the token it labels. This plan anchors each record to its
token, and it derives one grammar per sentence with exactly N records. It tests
three head representations under the seeded protocol. The roadmap holds this
work as phase P9.

- Implements: LRN-DELIVER without LRN-DELIVER-2 without LRN-DELIVER-3
- Defers: ENG-SPLIT
- Defers: EVL-TIERS
- Defers: IAC-APPLY

## Status

The code work can start after plan 006 merges: the schema module, the grammar
template, the harness, the pairs builder, and the tests. The campaign waits on
plan 008, because each run uses the winning recipe, and on the tolerance of
plan 007.

No decision blocks this plan. The change is a specification change to ENG-SCHEMA
and to the text of TRN-SFT-2. The Decisions section says why T2, T7, and T10
hold.

ENG-SCHEMA, TRN-SFT, and COR-AUG are done. The implementation change edits the
text of ENG-SCHEMA-1, ENG-SCHEMA-2, and TRN-SFT-2, and the units stay done. This
plan therefore cites none of them under `Implements:`, per the plans rule on a
done unit.

ENG-SPLIT stays partial. The harness gains the grammar renderer, and the Perl
tokenizer (ENG-SPLIT-1, ENG-SPLIT-2) waits for a later plan.

## Decisions

This plan changes no decision.

- Decision T2 holds. The output stays one GGUF at Q8_0 under greedy decoding and
  a GBNF grammar. The grammar derives from the input sentence and the template.
  The same bytes in give the same grammar, so determinism holds under the same
  three pins.
- Decision T7 holds. The harness renders the grammar and parses the records, and
  it stays the only caller of llama.cpp (ENG-SPLIT-4).
- Decision T10 holds. The anchors live in the model serialization only. The
  harness strips them, and the annotation contract does not expose them
  (ENG-CONTRACT-1).

The learning maps to FuguTTX D2 and to the FuguTTX harness rule that a tool call
obeys the harness schema at generation time. Constrain the structure that the
model gets wrong, not the vocabulary alone.

## The reason

From the P3 and P4 scorecards and the harness code:

1. `sft-cpt` failed 47 of 2001 ewt dev sentences and 46 of 2077 ewt eval
   sentences. A failed sentence counts every token wrong (`t1.py`). On ewt that
   is about 2 LAS points at zero model error, and `sft-base` lost 4.
2. The grammar is `root ::= record+`. The count check lives in the harness
   parse, after generation. The model can stop early or run long, and nothing at
   generation time prevents it.
3. UPOS 0.936, lemma 0.952, LAS 0.773 on the ewt dev split. The head and the
   deprel carry the error, and the per-field card of plan 006 splits the two.
4. A record holds no reference to its token. The model counts records to keep
   its place. It writes a head index that nothing checks against the sentence
   length until the parse.

## The design

The input serialization stays: one line per token with the index and the form,
then one empty line.

The output record gains an anchor: the token index, the form, then UPOS, lemma,
head, deprel, and feats, tab-separated. The harness derives one grammar per
sentence from `share/annotation.gbnf`. The template keeps the static
nonterminals `upos`, `lemma`, `deprel`, and `feats`. The harness writes the root
rule, and one rule per token with the literal anchor. It writes one head rule
per record, with the legal values of that record. Those are 0 to N without the
record's own index, so a self-head cannot occur. The harness writes each rule
with digit ranges split around the own index, so the grammar of a long sentence
stays small. For a three-token sentence:

```text
root ::= r1 r2 r3
r1 ::= "1\tFrom\t" upos "\t" lemma "\t" h1 "\t" deprel "\t" feats "\n"
h1 ::= "0" | "2" | "3"
```

A form escapes the double quote and the backslash in its literal.

Three head variants run under the seeded protocol:

- V0, the absolute index. Each head rule enumerates 0 to N without the own
  index.
- V1, the signed offset from the record index: `-3`, `+2`, and `R` for the root.
  Each head rule holds the offsets that stay inside the sentence. The harness
  converts to an index at parse time.
- V2, the index with the head form: `0:ROOT`, `1:From`, `2:Friday`, and so on.
  The grammar forces a legal pair, so the model picks a visible token, not a
  number.

The harness keeps the P3 serialization as the `flat` variant: no anchor, the
static template grammar, and the absolute index. The promoted model of P3 runs
through it until an anchored variant promotes. The configuration name carries
the variant of a candidate, and a `head` input carries it to the scoring path.

`schema.py` renders the template, the per-sentence grammar, the input, and the
records in Python, and `bin/stx` renders the same in Perl. A test proves the two
renderings agree byte for byte on the fixtures. A format drift between training
and inference fails in silence, and the test is the guard.

With the exact-count grammar, the `count` and `fields` failure kinds of plan 006
cannot occur. The `cutoff` kind stays, at the 4096-token cap, and the card
records it.

## The experiment card

- Hypothesis H4: the anchored V0 format ends the count and field failures. It
  raises the ewt dev LAS by about 2 points against the plan 008 winner.
- Hypothesis H5: V1 or V2 raises LAS on sentences over 20 tokens by more than
  the tolerance, against V0.
- Prediction: H4 holds. H5 holds for V2, and the length buckets of plan 006 show
  where.
- Seeds: 11, 23, and 37. Nine runs.
- Stop rule: a grammar that llama.cpp rejects on a long sentence ends that
  variant, and the batch records the sentence length. The dispatches stop two
  hours before the lease expires, and `down` runs.

## Order of work

1. Rewrite `schema.py`. `render_tokens` stays, `render_labels` gains the anchor,
   and a `render_grammar` function returns the per-sentence grammar text for one
   variant. `parse_records` of `judge.py` moves next to it and reads the anchor.
   `gbnf.py` parses the derived grammar with its escaped literals, and
   `test_schema.py` covers the derived grammar of each variant.
2. Rewrite the comment block and the template of `share/annotation.gbnf`. The
   file holds the static nonterminals and documents the derived rules.
3. Teach `bin/stx label` the same renderer in Perl. The exec transport passes
   the grammar text with `--grammar`, under the 128 KiB argument limit of Linux.
   The server transport sends it in the request body. A grammar above the limit
   goes through `--grammar-file` on the exec transport, and the batch records
   the longest inline grammar. The pledge target of EVL-SUITE-1 belongs to the
   artifact suite of a later plan. The parse strips the anchor and checks it
   against the input. A `--head` option selects the variant, `flat` included,
   and the promoted model fixes the default. The `score` verb, `train.yml`, and
   `t1.yml` gain a `head` input that reaches that option through the
   environment. `t/stx.t` covers the anchor strip, the input check, the `--head`
   option, and the inline grammar.
4. Add the byte-for-byte agreement test between the Perl and the Python
   renderers, on the fixtures under `packages/stx-corpus/tests/fixtures`.
5. Rebuild the pairs. `pairs.py` writes the anchored completion, once per
   variant: `pairs-v0.jsonl`, `pairs-v1.jsonl`, `pairs-v2.jsonl`, and the dev
   pairs of plan 006 for each. `upload.py` puts them in `stx-corpus`. The
   accepted teacher records rebuild through the same renderer.
6. Add three configurations from the plan 008 winner: `sft-v0.yml`,
   `sft-v1.yml`, and `sft-v2.yml`. The `sft` action of plan 006 runs each by
   name, and the `head` input names the variant at scoring.
7. Write the card. Read the price. Dispatch `up` with a ten-hour lease. For each
   seed and variant, dispatch the pass. Dispatch `gguf`, then `score`. Nine
   runs. Dispatch `down`.
8. Dispatch the tier T1 sweep on the median dev seed of each variant, with the
   matching `head` input. The median seed keeps the promote interval free of a
   selection gain. Dispatch the dev sweep of plan 006 on the same seed, so the
   promote verb finds its dev copy.
9. Analyze with the compare command of plan 006 against the plan 008 winner, per
   treebank, metric, and length bucket. Record the output tokens per sentence
   and the sweep wall clock of each variant. The anchor and the head form add
   output tokens.
10. Promote the best variant when it passes the promote rule of plan 006.
11. Update the specification. When an anchored variant promotes, retire the
    `flat` variant in the same change, and the ENG-SCHEMA text then describes
    the anchored format only. When none promotes, the anchored variants stay
    behind the `--head` option, and the text describes both, as below.
    ENG-SCHEMA-1 reads: a GBNF grammar from the schema template must constrain
    the model output. An anchored variant must derive the grammar per sentence,
    and it must force exactly one record per token. ENG-SCHEMA-2 reads: a record
    must carry UPOS, lemma, head, deprel, and feats. An anchored variant must
    prefix the record with the token index and the form. TRN-SFT-2 reads: the
    format must be a token list in, and grammar-constrained records out, in the
    variant of the promoted model. The ENG-SCHEMA prose of
    [the engine document](../../spec/engine.md) names that variant. Set the
    ENG-SCHEMA and ENG-SPLIT notes in [the register](../../spec/STATUS.md). Name
    the `head` input in the stage map of `train/RUNBOOK.md`.
12. Write LEARNING batch 5. The claims: the failure kinds before and after, and
    the paired effect of the anchor and of each head variant with its interval.
    Then the length-bucket rates, the output tokens per sentence, and the sweep
    wall clock. Add one row to
    [the library index](../../spec/LEARNING.md#lrn-map): grammar-anchored
    labeling, on the page `Library-FuguSTX-output-format`. The row rehearses
    FuguTTX D2 and the FuguTTX harness patterns.

## The budget

Nine runs of the plan 008 recipe. A run takes 15 to 30 minutes, because the
anchor adds about a third more output tokens and the recipe can hold three
epochs. Each run adds a 2-minute conversion and a 5-minute dev score with the
eight slots of plan 006. Three to seven hours on the H100-1-80G: EUR 9 to 20 at
the 2026-08-28 price. The ten-hour lease is the cap, and the stop rule keeps the
dispatches inside it. A forecast must not assume a run cheaper than one hour
(TRN-BUDGET-1).

## Out of scope

- The byte offsets and the model hash in the output (ENG-DETERM). A later plan.
- A lemma shortcut, for example a copy marker when the lemma equals the
  lowercased form. The open questions hold it.
- A feats redesign.
- A change to the scorecards of P3 and P4. They stay records under the `flat`
  serialization.

## Open questions

- The anchor form. The index alone anchors the count. The form costs output
  tokens: about a third more per sentence, on the CPU path of the product. The
  campaign measures the tokens and the wall clock, and the batch records the
  trade.
- The lemma field. A copy marker cuts tokens and a class of errors, and it
  changes the schema again. A later plan tests it on the anchored format.
- Grammar size. A 150-token sentence gives 150 record rules and 150 head rules.
  The V2 head rules enumerate the forms, so they grow fastest. The longest dev
  sentence measures the grammar size and the parse cost per variant.
