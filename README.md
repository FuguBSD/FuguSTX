# FuguSTX

An embeddable English linguistic analysis engine for prose linters, built as the
pilot of FuguTTX.

FuguSTX turns raw English text into offset-faithful linguistic annotations:
tokens, sentences, universal POS tags, lemmas, morphological features, and
dependency relations. A linter consumes the annotations and stays a rulebook.
The engine is a Qwen3-0.6B fine-tune under llama.cpp, on the CPU only. The `stx`
harness — Perl 5 over Fugu — computes every byte offset, and the model labels
the tokens.

The project is also the pilot of FuguTTX. The build rehearses the FuguTTX
production pipeline at small scale, on the same components, at real prices.
Cheap learnings are a deliverable.

The project is specification-first: the code follows the specification.

## Documentation

The specification in [spec/](spec/index.md) is the authoritative reference. Read
[spec/DECISIONS.md](spec/DECISIONS.md) before you make a plan.

## Commands

```sh
make check       # spec-check + ste-lint + test; run it before each commit
make prettier    # Markdown, JSON and YAML formatting check
make help        # list the targets
```

## Commit scopes

`spec`, `docs`, `engine`, `corpus`, `train`, `eval`, `infra`, `ci`.

## License

ISC. See [LICENSE](LICENSE).
