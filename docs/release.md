# Release Process

This repo publishes releases through GitHub Actions only.

Local commands prepare and validate the checked-in content. They do not publish tags, releases, or OCI artifacts.

## Release Flow

1. Prepare the release version in git.
2. Run the local validation checks.
3. Merge the release commit to `main`.
4. Trigger the release workflow manually in GitHub Actions.

## Prepare The Release Commit

Update the checked-in release version:

```bash
mise run release:prepare -- 1.0.1
```

You can inspect the accepted arguments with:

```bash
mise run release:prepare --help
```

That updates:

- [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json)
- [`.codex-plugin/plugin.json`](../.codex-plugin/plugin.json)
- [`.cursor-plugin/plugin.json`](../.cursor-plugin/plugin.json)

Then validate the release candidate:

```bash
mise run preflight
mise run ci
mise run artifact:check
```

If the release changes install docs or shared tool surfaces, also do the relevant manual spot checks from [docs/testing.md](./testing.md).

Commit the version bump and merge it to `main`.

## Trigger The Release

Releases are created by the `Release OCI Skills Artifact` workflow:

- Workflow file: [`.github/workflows/release-oci.yml`](../.github/workflows/release-oci.yml)
- Trigger type: manual `workflow_dispatch`
- Required input: `version`

In GitHub:

1. Open `Actions`.
2. Select `Release OCI Skills Artifact`.
3. Click `Run workflow`.
4. Enter the semver version without a leading `v`, such as `1.0.1`.
5. Run it from `main`.

The workflow rejects non-semver input, checks that the tag does not already exist, and requires the run to come from `main`.

## Recommended GitHub Repository Settings

Before relying on this release path, enable these repository protections:

- Secret Protection / secret scanning alerts
- Push protection for secrets
- Dependabot alerts
- A branch ruleset for `main`
- A tag ruleset for `v*`

Recommended `main` ruleset:

- require pull requests before merge
- require at least one approval
- require required status checks to pass
- block force pushes
- restrict deletions

Recommended `v*` tag ruleset:

- restrict creations
- restrict updates
- restrict deletions
- bypass only for the release automation app and a minimal admin escape hatch if needed

If your GitHub plan supports it, add custom secret-scanning patterns for Kong credential formats such as `kpat_` and `spat_`, and enable push protection for those patterns too.

## What The Workflow Does

The release workflow runs in three stages:

### Validate

- runs `mise run ci`
- verifies the requested version format
- verifies the Git tag does not already exist
- verifies checked-in manifest versions match the requested release version
- validates the OCI artifact packaging path

### Publish OCI Artifact

- builds the `scratch` OCI artifact from [Dockerfile.skills](../Dockerfile.skills)
- pushes the image to the configured ECR registry

The workflow currently skips CIS and SBOM actions for this artifact because it is a content-only `scratch` image whose payload is just the checked-in `skills/` tree. The release gate relies on checked-in review, `mise run ci`, and `mise run artifact:check`.

### Tag And Release

- creates the Git tag `v<version>`
- creates the GitHub release
- includes the published OCI image reference in the release notes

## Day-To-Day CI vs Release Validation

Use these commands for different levels of confidence:

- everyday repo validation: `mise run ci`
- packaging changes or release prep: `mise run artifact:check`
- full release candidate: `mise run preflight`, `mise run ci`, `mise run artifact:check`

## Pinning Notes

This repo already pins the highest-risk automation surfaces:

- GitHub Actions are pinned by commit SHA
- Python dependencies are locked in `uv.lock`

Remaining caveat:

- `mise run ci` calls the `gh` CLI available on the runner image, so the exact GitHub CLI version is not pinned by the workflow itself

## Troubleshooting

- If `mise run ci` fails on `gh skill publish --dry-run`, fix the reported skill metadata or repository publishability issue before merging.
- If `mise run artifact:check` fails, inspect [Dockerfile.skills](../Dockerfile.skills), [.dockerignore](../.dockerignore), and the `skills/` tree.
- If the release workflow fails at the version check, rerun [scripts/release_prepare.py](../scripts/release_prepare.py) with the exact target version and recommit the manifest changes.
