# Tool Choice And Safety

Use this file when the task is moving from diagnosis into implementation or can
change live state.

## Tool Preference

- Use MCP for live Konnect inspection and analytics.
- Use `skills/deck-gateway/SKILL.md` for `decK`-managed Gateway declarative
  workflows.
- Use `skills/terraform-konnect/SKILL.md` or
  `skills/terraform-kong-gateway/SKILL.md` for Terraform-managed resources.
- Use `skills/kongctl-query/SKILL.md` or
  `skills/kongctl-declarative/SKILL.md` when the repo already centers on
  `kongctl` or the user explicitly asks for it.

## Safety Defaults

- Preserve the user's existing toolchain instead of converting them mid-task.
- Prefer inspect, validate, diff, or plan boundaries before any apply or sync.
- Require explicit confirmation before production-impacting or mutating steps.
- Restate the target org, region, control plane, workspace, or environment
  before a mutating step when scope might be ambiguous.
