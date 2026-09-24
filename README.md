# FuguSTX

FuguSTX finds the tells of machine-written prose in English technical text,
built as the pilot of FuguTTX. The engine reads a document and reports one
finding per sentence: the byte offsets, a verdict, and a tell category. A tool
or an agent repairs the text from the findings.

The engine is a Qwen3-0.6B fine-tune under llama.cpp, on the CPU only. The model
learns from pairs of a human document and a machine mirror of the same facts.
The `stx` harness, Perl 5 over Fugu, computes every byte offset. The build
rehearses the FuguTTX production pipeline at small scale.

## Commands

```sh
make setup                 # install the development tools into .venv
make deps                  # install gitleaks, the Scaleway CLI and OpenTofu
make check                 # run every gate; run it before each commit
make test                  # run the test suite
make format-fix            # fix the Python, Markdown, JSON and YAML formatting
make infra-up STACK=<s>    # apply one infra stack; billing starts here
make infra-down STACK=<s>  # destroy one infra stack; billing stops here
make infra-status          # list the live resources
make train-cpt             # run one continued pretraining pass
make train-sft             # run one supervised fine-tuning pass
make scorecards            # print the evaluation scorecards
```
