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
make deps        # install gitleaks, the Scaleway CLI and OpenTofu
make check       # every gate; run it before each commit
```

`make deps` installs the `tool` environment before the `runtime` environment, so
the gitleaks binary of the secret gate is present for each chain.
`deps/SHA256.txt` records the sha256 digest of each versioned download, and
`make deps` compares the downloaded bytes against it. The CI gate installs
gitleaks with `make deps`, so one pin serves the operator gate and the CI gate.

`make check` runs the Markdown format gate, and prettier runs through bunx. The
operator installs bun, for example from Homebrew. The manifest does not provide
it, because the format gate needs `bunx` before a target can run.

## Commit scopes

`spec`, `docs`, `engine`, `corpus`, `train`, `eval`, `infra`, `ci`.

## License

ISC. See [LICENSE](LICENSE).
