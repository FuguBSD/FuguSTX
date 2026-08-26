locals {
  code = "stx"
}

# No resource exists yet: IAC-DEVHOST waits on the KVM test result. When a
# resource lands, build its `<code>:stack`/`<code>:managed`/`<code>:lifecycle`
# tags from one map here, per the shared tag rule.
