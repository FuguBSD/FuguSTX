# The learning register

This document specifies the learning register. The register records what each
campaign teaches about the FuguTTX specification. The
[implementation register](STATUS.md) is a different document, and it records
implementation state.

<a id="reg-deliver"></a>

## The register is a deliverable

The register is the deliverable of G2, per decision [T11](DECISIONS.md#t11).

- **REG-DELIVER-1** — Every campaign must end with a register entry that maps
  its outcome to FuguTTX specification units.
- **REG-DELIVER-2** — A finding must land in the FuguTTX `docs/research/`
  directory.
- **REG-DELIVER-3** — A finding that contradicts the FuguTTX specification must
  become a FuguTTX specification change, not a note.

<a id="reg-map"></a>

## The planned rehearsals

Each row of the table is a planned rehearsal, and each campaign appends
findings. One row exists for each pilot component. "The shared instructions"
names the synced [infra/CLAUDE.md](../infra/CLAUDE.md).

| Pilot component                                | FuguTTX units rehearsed                             |
| ---------------------------------------------- | --------------------------------------------------- |
| H100 quota request and grant time              | FuguTTX IAC-TRAIN, FuguTTX IAC-PREREQ               |
| Live price read before apply                   | FuguTTX IAC-PREREQ, the shared instructions         |
| State backend, native lock, encryption         | The shared instructions                             |
| Three-application credential split             | The shared instructions, FuguTTX D9                 |
| Train key over SSH, expiry backstop            | The shared instructions                             |
| Watchdog, heartbeat, claim protocol            | The shared instructions                             |
| Train stack up/down, teardown completeness     | FuguTTX IAC-TRAIN, the shared instructions          |
| Checkpoint sync per epoch                      | FuguTTX IAC-DURA, FuguTTX TRN-EXEC                  |
| Axolotl in Docker on the GPU OS image          | FuguTTX TRN-EXEC, FuguTTX D3                        |
| CPT and SFT passes end to end                  | FuguTTX TRN-CPT, FuguTTX TRN-SFT, FuguTTX D4        |
| Qwen3-32B under vLLM, SSH tunnel, judge filter | FuguTTX TRN-AUG, FuguTTX D4                         |
| Corpus lanes and bucket policies               | FuguTTX IAC-PERSIST, FuguTTX D6                     |
| KVM test and dev host selection                | FuguTTX IAC-METAL, FuguTTX IAC-DEV, FuguTTX D9      |
| Guest image build with fuguvm and autoinstall  | FuguTTX IAC-IMAGE                                   |
| llama.cpp on OpenBSD, CPU only, determinism    | FuguTTX D2, and the FuguTTX inference specification |

<a id="reg-scope"></a>

## The scope of a claim

The register must scope every claim, because these FuguTTX risks stay open after
the pilot:

- The author-copyright eval lane, and its licensing handling. Every FuguSTX
  input carries [a permissive license](licensing.md#lic-lic).
- Training dynamics at 4B: multi-hour epochs, checkpoint sizes that stress the
  bucket rules, catastrophic forgetting, and replay mixes.
- Agentic traces: tool calls, rollouts against mutable guests, and the
  fabricated-observation risk. The guests of the pilot
  [verify an artifact](evaluation.md#evl-suite), and they never host an agent.
- RAG, variants, and personas.

A 0.6B result does not predict a 4B result. The register must say what a finding
is evidence for, and what it is not.
