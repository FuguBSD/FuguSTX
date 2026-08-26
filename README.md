# FuguSTX

An embeddable English linguistic analysis engine for prose linters, built as the
pilot of FuguTTX.

FuguSTX turns raw English text into offset-faithful linguistic annotations:
tokens, sentences, universal POS tags, lemmas, morphological features, and
dependency relations. A linter consumes the annotations and stays a rulebook.

The engine is a Qwen3-0.6B fine-tune under llama.cpp, on the CPU only. The `stx`
harness — Perl 5 over Fugu — computes every byte offset, and the model labels
the tokens.

The build rehearses the FuguTTX production pipeline at small scale, on the same
components, at real prices. Cheap learnings are a deliverable.

## Documentation

The project is specification-first: the specification in [spec/](spec/index.md)
is the authoritative reference.

## Commands

```sh
make deps        # install the Scaleway CLI
make check       # spec-check + ste-lint + test; run it before each commit
make format-md   # Markdown, JSON and YAML formatting check
```

## Commit scopes

`spec`, `docs`, `engine`, `corpus`, `train`, `eval`, `infra`, `ci`.

## License

ISC. See [LICENSE](LICENSE).
