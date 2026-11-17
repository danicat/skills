---
name: google-oss
description: >
  Compliance and licensing guide for Google Open Source repositories and
  personal open-source projects published by Googlers. Enforces source file
  license headers (such as Apache-2.0) using addlicense, verifies license files,
  inserts required non-official product disclaimers, and audits pre-release
  compliance. Activate when preparing Google Open Source or Googler personal
  projects for release, applying copyright headers, or adding required
  disclaimers.
license: Apache-2.0
metadata:
  category: coding
  tags: "google, oss, licensing, copyright, compliance"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  catalog: https://skills.danicat.dev
---

# Google open-source compliance and licensing

Audit, apply, and verify Google Open Source policy requirements, source code license headers with `addlicense`, and mandatory repository disclaimers.

## Available scripts

- **[scripts/apply-license.sh](scripts/apply-license.sh)**: Cross-platform helper that resolves `addlicense` from `$PATH`, `$GOBIN`, or `$GOPATH/bin` (installing it automatically when missing), ignores generated and vendored directories safely (`vendor/`, `node_modules/`, `.venv/`, `third_party/`, `_site/`, `*.pb.go`), and supports both apply and read-only `--check` modes.

```bash
# Inspect options and usage
bash scripts/apply-license.sh --help

# Apply headers to a corporate Google Open Source repo
bash scripts/apply-license.sh -c "Google LLC" .

# Apply headers to a personal open-source repo
bash scripts/apply-license.sh -c "Jane Doe" -l apache src/

# Verify header coverage in CI without modifying files
bash scripts/apply-license.sh --check -c "Google LLC" .
```

Flags:
- `-h`, `--help`: Show usage and exit cleanly.
- `--check`: Audit existing headers and exit non-zero if any matching file lacks one.
- `-c`, `--holder`: Copyright holder string (defaults to `Google LLC`).
- `-l`, `--license`: License type: `apache` (default), `bsd`, `mit`, or `mpl`.
- `-y`, `--year`: Copyright year passed to `addlicense -y`.
- `-s`, `--spdx-only`: Emit SPDX short-form identifiers only.
- `-i`, `--ignore`: Add extra ignore globs (repeatable).
- `--no-default-ignores`: Skip built-in build and vendor ignore patterns.

## Choosing the right copyright holder

> [!IMPORTANT]
> Always inspect the root `LICENSE` file and existing source headers before applying or checking copyright banners:
> - **Corporate Google Open Source repositories** (`github.com/google/*`, `googleapis/*`, `GoogleCloudPlatform/*`, or Google-owned projects): use `-c "Google LLC"`.
> - **IARC-approved personal projects owned by a Googler**: use `-c "<Author Name>"` so you never overwrite personal copyright with `"Google LLC"`, while still adding the required non-official Google product disclaimer to `README.md`.

## Applying and checking headers directly with addlicense

Install `addlicense` via Go when calling the binary directly:

```bash
go install github.com/google/addlicense@latest
```

Resolve `addlicense` across `$PATH`, `GOBIN`, and `GOPATH`:

```bash
ADDLICENSE="${GOBIN:-$(go env GOBIN)}"
ADDLICENSE="${ADDLICENSE:+${ADDLICENSE}/addlicense}"
ADDLICENSE="${ADDLICENSE:-$(go env GOPATH)/bin/addlicense}"
command -v addlicense >/dev/null 2>&1 && ADDLICENSE="addlicense"

# Apply Apache-2.0 headers while skipping third-party trees
"$ADDLICENSE" -c "Google LLC" -l apache \
  -ignore "vendor/**" -ignore "node_modules/**" -ignore ".venv/**" .

# Audit without editing files (CI check)
"$ADDLICENSE" -check -c "Google LLC" -l apache \
  -ignore "vendor/**" -ignore "node_modules/**" -ignore ".venv/**" .
```

Common `addlicense` flags:
- `-l apache`: Apache License 2.0 (standard default).
- `-l mit` or `-l bsd`: MIT or BSD 3-Clause header format.
- `-s=only`: Short SPDX identifier only (`// SPDX-License-Identifier: Apache-2.0`).
- `-ignore "vendor/**"`: Exclude third-party or generated files such as `*.pb.go`.

## Required README disclaimers

Every repository published by Googlers or under Google Open Source that is not an official Google product needs the matching disclaimer at the bottom of `README.md`.

### Standard non-official product disclaimer

```markdown
---

## Disclaimer

This is not an officially supported Google product.
```

### Experimental or educational project disclaimer

```markdown
---

## Disclaimer

This is not an officially supported Google product. It is an experimental project created for educational and development purposes.
```

## Pre-release compliance checklist

1. **License header coverage**: Run `scripts/apply-license.sh --check` (or `addlicense -check`) across `.go`, `.py`, `.ts`, `.js`, `.rs`, `.c`, `.cpp`, `.sh`, and `.proto` files, confirming generated and third-party files stay excluded.
2. **Root `LICENSE` file**: Confirm an unmodified text copy of the chosen license exists at the repository root.
3. **Copyright holder accuracy**: Verify the header holder matches corporate (`Google LLC`) or personal ownership rules.
4. **Non-official product disclaimer**: Confirm the `## Disclaimer` section appears at the bottom of `README.md`.
5. **Zero internal leaks**: Verify there are no internal URLs, internal bug trackers, corporate credentials, or non-public codenames.

## References

- [License header formats](references/license-headers.md): Comment styles for Apache 2.0, MIT, BSD 3-Clause, and SPDX short identifiers.
- [Disclaimer templates](references/disclaimers.md): Standard, sample-code, experimental, and maintenance notices.
