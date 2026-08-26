locals {
  code = "stx"
}

# No resource exists yet: IAC-IMAGE waits on phase P5. When a resource
# lands, build its `<code>:stack`/`<code>:managed`/`<code>:lifecycle` tags
# from one map here, per the shared tag rule.
