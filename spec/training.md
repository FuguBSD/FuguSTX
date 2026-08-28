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
- **TRN-INST-2** — [LEARNING](LEARNING.md#lrn-deliver) must record the response
  time of the quota request.

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
[annotation schema](engine.md#eng-schema) defines the output grammar. Rehearses:
FuguTTX TRN-SFT.

- **TRN-SFT-1** — The SFT pass must train on treebank-derived pairs, plus
  [accepted augmentation](corpus.md#cor-aug).
- **TRN-SFT-2** — The format must be a token list in, and grammar-constrained
  labels out.
- **TRN-SFT-3** — The treebank pairs must come from the train splits. The dev
  split is a score input, and it must not enter a pair.

<a id="trn-teach"></a>

## The teacher campaign and the judge filter

The teacher proposes, and a verifier disposes ([T5](DECISIONS.md#t5)). The SSH
tunnel is the FuguTTX transport, rehearsed exactly. FuguTTX stakes its data
quality on the same filter pattern, so the filter results are LEARNING entries.
Rehearses: FuguTTX TRN-AUG.

The judge filter applies three checks to each proposed record:

1. Two independent teacher passes agree on the annotation.
2. The dependency tree validates: one root, fully connected.
3. Every tag is in the UD inventory, and
   [the lexicon check](engine.md#eng-lexicon) passes.

- **TRN-TEACH-1** — vLLM must serve Qwen3-32B on the train instance.
- **TRN-TEACH-2** — The endpoint must bind to localhost.
- **TRN-TEACH-3** — The harness must reach the endpoint over an SSH tunnel.
- **TRN-TEACH-4** — The judge filter must accept a record only when the three
  checks pass.
- **TRN-TEACH-5** — The filter must log each rejected record with its reason.
- **TRN-TEACH-6** — LEARNING must record the filter design and the rejection
  rates.

<a id="trn-exec"></a>

## Execution

A destroy loses at most one epoch, which is minutes at this scale. Rehearses:
FuguTTX TRN-EXEC, FuguTTX IAC-DURA.

- **TRN-EXEC-1** — Training must run in the published Axolotl CUDA Docker image.
- **TRN-EXEC-2** — Every configuration must live in the repository.
- **TRN-EXEC-3** — A run must be `make train-cpt` or `make train-sft` against a
  provisioned instance.
- **TRN-EXEC-4** — Checkpoints must synchronize to Object Storage after each
  epoch.

<a id="trn-budget"></a>

## The compute budget

The estimates are order-of-magnitude, at the H100 price of EUR 2.87 per hour,
read 2026-08-28. Scaleway documents a minimum of 60 minutes per created
resource.

| Item                               | GPU-hours | EUR per run |
| ---------------------------------- | --------- | ----------- |
| SFT pass (0.6B, QLoRA)             | 1–2       | 3–6         |
| CPT rehearsal pass                 | 1–2       | 3–6         |
| Teacher campaign (Qwen3-32B, vLLM) | 5–15      | 14–43       |
| Artifact suite sweep (dev host)    | —         | 1–3         |

The last row prices [the artifact suite](evaluation.md#evl-suite) sweep on
[the dev host](infrastructure.md#iac-devhost). An active month costs
approximately EUR 50–150. [The cap](infrastructure.md#iac-apply) is EUR 300 per
month, and only a human raises it. The FuguTTX specification prices one campaign
month at EUR 300–800. The pilot buys its rehearsals at approximately a tenth of
the flagship price.

- **TRN-BUDGET-1** — A cost estimate must not assume a run cheaper than one
  hour.
