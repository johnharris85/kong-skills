# Security Policy

## Reporting A Vulnerability

Do not open a public GitHub issue for suspected security problems.

If you believe you have found a security vulnerability in this repository, the published skill payloads, or the install metadata, report it privately to `vulnerability@konghq.com`.

Include:

- a description of the issue
- the affected file, workflow, or install surface
- reproduction steps or proof of concept
- the potential impact

## Scope Notes

This repository publishes instruction content, install metadata, and an OCI artifact. Reports that involve supply-chain, release, workflow, or packaging issues are in scope.

## Recommended GitHub Repository Protections

For the public release path used by this repository, we recommend enabling these repository settings:

- Secret Protection / secret scanning alerts
- Push protection for secrets
- A branch ruleset for `main`
- A tag ruleset for release tags matching `v*`
- Dependabot alerts

Recommended `main` protections:

- require pull requests before merge
- require approvals
- require required status checks to pass
- block force pushes
- restrict deletions

Recommended `v*` tag protections:

- restrict creations except for the release automation app
- restrict updates
- restrict deletions

If your GitHub plan supports custom secret-scanning patterns, add repository or organization patterns for Kong-specific credentials such as `kpat_` and `spat_`, and enable push protection for those patterns.

If your GitHub plan supports delegated bypass for push protection, prefer a small reviewer/bypass group instead of allowing routine bypass by any writer.

See [docs/release.md](docs/release.md) for how these protections fit the release workflow.

## Pinning Posture

This repository prefers pinned execution surfaces where practical:

- GitHub Actions are pinned by commit SHA in workflow files
- Python dependencies are locked in `uv.lock`
- The OCI artifact is built from a minimal `scratch` base

Current caveats:

- the CI workflow uses the `gh` CLI provided by the GitHub runner image, so the exact `gh` version is not pinned in-workflow
- the repo-managed Python toolchain is pinned to a Python release line in `mise.toml`, but maintainers should still review version changes when updating it

## Disclosure

Please use coordinated disclosure. Avoid public discussion until Kong has had a reasonable opportunity to investigate and remediate the issue.
