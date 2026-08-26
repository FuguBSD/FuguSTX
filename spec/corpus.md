# Corpus

<a id="cor-buckets"></a>

## The buckets

Four buckets hold the data of the pilot. The set mirrors the FuguTTX bucket set.
Rehearses: FuguTTX IAC-PERSIST, FuguTTX D6.

- **COR-BUCKETS-1** — The project must use four buckets: `stx-corpus`,
  `stx-evalcorpus`, `stx-checkpoints`, and `stx-artifacts`.
- **COR-BUCKETS-2** — Each bucket must apply the same versioning and lifecycle
  rules as the FuguTTX bucket set.

<a id="cor-lanes"></a>

## The lanes

Two lanes split the corpus ([T6](DECISIONS.md#t6)). Contamination drives the
lane rule here, and author copyright drives it in FuguTTX D6. The mechanics are
identical, so the rehearsal is faithful.

- **COR-LANES-1** — The training lane must hold the train and dev splits of UD
  English EWT and GUM, filtered per [the sources](#cor-sources).
- **COR-LANES-2** — The training lane must also hold a prose lane for
  [the CPT rehearsal](training.md#trn-cpt): public-domain and CC-BY grammar
  prose.
- **COR-LANES-3** — The eval lane must hold the UD test splits, plus PUD.
- **COR-LANES-4** — The lane rule is absolute: eval data must not enter
  training.

<a id="cor-sources"></a>

## The sources

The treebanks come from the Universal Dependencies (UD) project. The current UD
release is 2.18 (2026-05-15), with the git tag `r2.18` in each treebank
repository. The table shows the state at the time of publication. Confirm the
release before each campaign.

| Treebank | Repository                                                                | Files                        | License              | Sentences | Words   |
| -------- | ------------------------------------------------------------------------- | ---------------------------- | -------------------- | --------- | ------- |
| EWT      | [UD_English-EWT](https://github.com/UniversalDependencies/UD_English-EWT) | `en_ewt-ud-{train,dev,test}` | CC BY-SA 4.0         | 16,622    | 254,820 |
| GUM      | [UD_English-GUM](https://github.com/UniversalDependencies/UD_English-GUM) | `en_gum-ud-{train,dev,test}` | Mixed; COR-SOURCES-3 | 14,353    | 256,739 |
| PUD      | [UD_English-PUD](https://github.com/UniversalDependencies/UD_English-PUD) | `en_pud-ud-test`             | CC BY-SA 3.0         | 1,000     | 21,180  |

PUD holds one test split only, so it serves the eval lane alone. The sibling
treebank UD_English-GUMReddit ships masked text, and it is not a source.

- **COR-SOURCES-1** — The pipeline must pin each treebank to one UD release tag,
  and it must record the tag.
- **COR-SOURCES-2** — The pipeline must fetch each `.conllu` file from the
  treebank repository at the pinned tag, for example
  `https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/r2.18/en_ewt-ud-train.conllu`.
- **COR-SOURCES-3** — The wikiHow and the fiction documents of GUM carry CC
  BY-NC-SA 4.0. The pipeline must exclude each GUM document with a
  non-commercial license, per [LIC-RELEASE-4](licensing.md#lic-release). The
  [GUM license file](https://raw.githubusercontent.com/UniversalDependencies/UD_English-GUM/r2.18/LICENSE.txt)
  names the license of each source.
- **COR-SOURCES-4** — The prose lane must hold these public-domain books from
  Project Gutenberg: [37134](https://www.gutenberg.org/ebooks/37134), The
  Elements of Style; [6409](https://www.gutenberg.org/ebooks/6409), How to Speak
  and Write Correctly; and [45814](https://www.gutenberg.org/ebooks/45814), An
  Advanced English Grammar.
- **COR-SOURCES-5** — The pipeline must strip the Project Gutenberg header and
  footer from each book.

<a id="cor-conllu"></a>

## The data format

A treebank file is CoNLL-U, per
[the UD format specification](https://universaldependencies.org/format.html). A
token line holds ten tab-separated columns: ID, FORM, LEMMA, UPOS, XPOS, FEATS,
HEAD, DEPREL, DEPS, and MISC. A `# sent_id` comment and a `# text` comment
precede each sentence. This sample from EWT holds the multiword token `Friday's`
on a range line:

```
# sent_id = weblog-juancole.com_juancole_20040604210986_ENG_20040604_210986-0001
# text = From Friday's Daily Star
1	From	from	ADP	IN	_	5	case	5:case	_
2-3	Friday's	_	_	_	_	_	_	_	_
2	Friday	Friday	PROPN	NNP	Number=Sing	5	nmod:poss	5:nmod:poss	_
3	's	's	PART	POS	_	2	case	2:case	_
4	Daily	Daily	ADJ	NNP	Degree=Pos	5	amod	5:amod	_
5	Star	Star	PROPN	NNP	Number=Sing	0	root	0:root	_
```

The reader turns a treebank file into training pairs. These rules keep the pairs
faithful to [the schema](engine.md#eng-schema) and to the harness offsets
([ENG-SPLIT](engine.md#eng-split)).

- **COR-CONLLU-1** — The reader must take the raw sentence text from the
  `# text` comment, and it must not rebuild the text from the FORM column.
  `SpaceAfter=No` in MISC states the spacing inside the text.
- **COR-CONLLU-2** — A range ID line (`2-3`) marks a multiword token, and it
  carries no annotation. The reader must expand the range, and it must exclude
  the range line from the label targets.
- **COR-CONLLU-3** — The DEPS column and a decimal ID line (`5.1`) belong to the
  enhanced graph. The reader must strip both: the schema holds basic
  dependencies only.
- **COR-CONLLU-4** — The reader must strip the GUM extra payload: `# meta::`
  comments, `global.Entity` comments, and the discourse and entity tags in MISC.
- **COR-CONLLU-5** — A FORM can hold the literal underscore, and EWT holds five
  such tokens. The reader must not treat that FORM as an empty field.

<a id="cor-aug"></a>

## Augmentation

The augmentation set holds teacher-generated technical and instructional
sentences, with proposed annotations.

- **COR-AUG-1** — A record must enter the training lane only through
  [the judge filter](training.md#trn-teach).
- **COR-AUG-2** — Each record must carry a provenance tag.
