# Training

<a id="trn-inst"></a>

## Instances

Two instance offers serve the training runs. Rehearses: FuguTTX IAC-TRAIN,
FuguTTX TRN-INST.

| Instance   | GPU          | VRAM  | EUR/hour | Role                       |
| ---------- | ------------ | ----- | -------- | -------------------------- |
| H100-1-80G | 1× H100 PCIe | 80 GB | 2.8665   | Default; hosts the teacher |
| L40S-1-48G | 1× L40S      | 48 GB | 1.4699   | Budget runs, no teacher    |

The 2026-08-28 price read fills this table, and a table price goes stale: only
the pre-apply read of TRN-INST-1 counts. A quota grant is per Organization:
probe each declared offer before a campaign, and record the result in the
runbook.

- **TRN-INST-1** — The pipeline must read the live price before it creates a
  resource.
- **TRN-INST-2** — [LEARNING](LEARNING.md#lrn-deliver) must record the quota
  state of each declared offer, and the response time of each quota request.

<a id="trn-cpt"></a>

## The CPT rehearsal

The pass exists to rehearse `make train-cpt` end to end ([T4](DECISIONS.md#t4)).
The dev-split comparison of TRN-CPT-2 can run on the train instance GPU, and its
scorecard records the device. Decision [T2](DECISIONS.md#t2) binds the shipped
engine and the tier T1 gate, and both stay on the CPU. Rehearses: FuguTTX
TRN-CPT.

- **TRN-CPT-1** — The CPT rehearsal must run one epoch, at a low learning rate,
  on [the prose lane](corpus.md#cor-lanes).
- **TRN-CPT-2** — When the pass does not move the scores, the product must drop
  the pass.
- **TRN-CPT-3** — When the product drops the pass, LEARNING must record why.

<a id="trn-sft"></a>

## The SFT pass

The SFT pass follows the CPT rehearsal (decision T4). The
[finding schema](engine.md#eng-schema) defines the output grammar. Rehearses:
FuguTTX TRN-SFT.

- **TRN-SFT-1** — The SFT pass must train on the admitted pairs of
  [the training lane](corpus.md#cor-lanes).
- **TRN-SFT-2** — The format must be segments in, and grammar-constrained
  findings out.
- **TRN-SFT-3** — The pairs must come from the train splits. The dev split is a
  score input, and it must not enter a pair.

<a id="trn-teach"></a>

## The generator campaign and the judge filter

The generator proposes, and the judge disposes ([T5](DECISIONS.md#t5)). The SSH
tunnel is the FuguTTX transport, rehearsed exactly. FuguTTX stakes its data
quality on the same filter pattern, so the filter results are LEARNING entries.
Rehearses: FuguTTX TRN-AUG.

The served checkpoint is `Qwen/Qwen3-32B-FP8`, the official FP8 release. The
BF16 weights hold near 65 GB, and the KV cache gets thin headroom on 80 GB.
Every client request turns the Qwen3 thinking mode off. The mirror must hold
prose only, and any thinking trace in the mirror enters the containment check.
The generation call samples at temperature 0.9, with a seed from the run and the
batch. A re-run of one batch therefore repeats its mirrors. A generator prompt
must hold no sentence of any human document of the corpus.

The judge filter applies four checks to each proposed pair:

1. The generator has not memorized the human document. A recall probe of the
   generator, or the n-gram containment of a source-only draft against the
   document, stays under the threshold.
2. The mirror holds no sentence of the original: the n-gram containment of the
   mirror against the document stays under the threshold.
3. The mirror follows the structure of the document: the section skeleton
   matches, the segment count stays within the bound, and the document renders.
4. The alignment labels pass. A labeler of a different model family than the
   generator proposes each label, and two seeded passes agree. The mechanical
   check of each category passes.

The labeler sees the segmented original and the segmented mirror, both numbered.
It returns the counterpart index of each mirror segment, or none, and a label
from the tell inventory of [the finding schema](engine.md#eng-schema). Qwen3-32B
labels the mirrors of the second generator, and a model of the family of the
second generator labels the Qwen3-32B mirrors.

The experiment card of the first corpus campaign fixes each threshold and each
bound, and this document holds no guess (TRN-TEACH-10).

- **TRN-TEACH-1** — vLLM must serve the Qwen3-32B generator on the train
  instance.
- **TRN-TEACH-2** — The endpoint must bind to localhost.
- **TRN-TEACH-3** — The generation client must reach the endpoint over an SSH
  tunnel.
- **TRN-TEACH-4** — The judge filter must admit a pair only when the four checks
  pass.
- **TRN-TEACH-5** — The filter must log each rejected pair with its reason.
- **TRN-TEACH-6** — LEARNING must record the filter design and the rejection
  rates.
- **TRN-TEACH-7** — A generator of a second model family must write a share of
  the mirrors through a headless client session under a dedicated profile. The
  profile must carry no rule file, no memory, and no tool except the output
  write.
- **TRN-TEACH-8** — A labeler of a different model family than the generator of
  the pair must propose each alignment label. It must run two passes with
  distinct seeds.
- **TRN-TEACH-9** — The judge must drop the target of a segment whose two passes
  disagree. It must reject a pair whose share of dropped segments exceeds the
  bound.
- **TRN-TEACH-10** — The experiment card of the first corpus campaign must state
  each threshold and each bound of the judge before the first admission. This
  document must hold each value after that campaign. A value in this document
  before that campaign is a guess, and the specification must not hold a guess.

<a id="trn-exec"></a>

## Execution

A destroy loses at most one epoch, which is minutes at this scale. The gguf step
uploads each converted artifact to the checkpoint bucket at once, so the promote
step needs no instance. Rehearses: FuguTTX TRN-EXEC, FuguTTX IAC-DURA.

- **TRN-EXEC-1** — Training must run in the published Axolotl CUDA Docker image.
- **TRN-EXEC-2** — Every configuration must live in the repository.
- **TRN-EXEC-3** — A run must be `make train-cpt` or `make train-sft` against a
  provisioned instance.
- **TRN-EXEC-4** — Checkpoints must synchronize to Object Storage after each
  epoch.
- **TRN-EXEC-5** — The promote step must copy the scored GGUF from the
  checkpoint bucket to the artifacts bucket. The artifact must match the dev
  scorecard `model_hash`.

<a id="trn-budget"></a>

## The compute budget

The estimates are order-of-magnitude, at the H100 price of EUR 2.87 per hour,
read 2026-08-28. Scaleway documents a minimum of 60 minutes per created
resource.

| Item                                 | GPU-hours | EUR per run |
| ------------------------------------ | --------- | ----------- |
| SFT pass (0.6B, QLoRA)               | 1–2       | 3–6         |
| CPT rehearsal pass                   | 1–2       | 3–6         |
| Generator campaign (Qwen3-32B, vLLM) | 5–15      | 14–43       |
| Artifact suite sweep (dev host)      | —         | 1–3         |

The last row prices [the artifact suite](evaluation.md#evl-suite) sweep on
[the dev host](infrastructure.md#iac-devhost). An active month costs
approximately EUR 50–150. [The cap](infrastructure.md#iac-apply) is EUR 300 per
month, and only a human raises it. The FuguTTX specification prices one campaign
month at EUR 300–800. The pilot buys its rehearsals at approximately a tenth of
the flagship price.

- **TRN-BUDGET-1** — A cost estimate must not assume a run cheaper than one
  hour.
- **TRN-BUDGET-2** — A generator that runs outside the train instance must
  record its call count and its token count per campaign. A campaign must state
  its call budget before the first call.
