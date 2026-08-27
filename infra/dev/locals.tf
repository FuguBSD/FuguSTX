locals {
  code = "stx"
}

# No resource exists yet: phase P5 adds the dev host. IAC-DEVHOST-6 states
# what its offer must run. When a resource lands, build its
# `<code>:stack`/`<code>:managed`/`<code>:lifecycle` tags from one map here,
# per the shared tag rule.
