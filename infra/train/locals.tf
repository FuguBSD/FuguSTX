locals {
  code = "stx"
}

# No resource exists yet: phase P3 adds the train stack. When a resource
# lands, build its `<code>:stack`/`<code>:managed`/`<code>:lifecycle` tags
# from one map here, per the shared tag rule.
