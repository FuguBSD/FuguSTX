# FuguSTX

An embeddable English linguistic analysis engine for prose linters, built as the
pilot of FuguTTX. FuguSTX turns raw English text into offset-faithful
annotations: tokens, sentences, POS tags, lemmas, features, and dependencies. A
linter consumes the annotations and stays a rulebook.

The engine is a Qwen3-0.6B fine-tune under llama.cpp, on the CPU only. The `stx`
harness, Perl 5 over Fugu, computes every byte offset, and the model labels the
tokens. The build rehearses the FuguTTX production pipeline at small scale.

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

## Commit scopes

`spec`, `docs`, `engine`, `corpus`, `train`, `eval`, `infra`, `ci`.
