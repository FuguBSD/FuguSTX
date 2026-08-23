# mk/local.mk: the consumer hook of this repository (MK-LOCAL).
# sync never touches this file.

# Install the external dependencies from deps/<OS>.txt: the Scaleway
# CLI into ~/.local/bin.
deps:
	scripts/deps runtime

.PHONY: deps
