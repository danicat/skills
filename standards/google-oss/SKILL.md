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
  category: standards
  tags: "google, open-source, licensing, compliance, standards, copyright"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.1"
  canonical: https://skills.danicat.dev/standards/google-oss/
---

# Google Open Source Compliance & License Attributions

Audit, apply, and verify Google Open Source policy requirements, source code license headers (`addlicense`), and mandatory repository disclaimers.

---

## ⚡ Quick Reference: Actions & Commands

### 1. Apply License Headers via `addlicense`

Install the official Google `addlicense` tool if not already present:

```bash
go install github.com/google/addlicense@latest
```

Apply Apache-2.0 copyright headers across all source files:

```bash
$(go env GOPATH)/bin/addlicense -c "Google LLC" -l apache .
```

Verify/Check without modifying (CI gate):

```bash
$(go env GOPATH)/bin/addlicense -check -c "Google LLC" -l apache .
```

Common license flag options:
- `-l apache`: Apache License 2.0 (standard default for Google OSS)
- `-l mit`: MIT License
- `-l bsd`: BSD 3-Clause License
- `-s=only`: Force SPDX short identifier style (`// SPDX-License-Identifier: Apache-2.0`)
- `-ignore "vendor/**"`: Ignore specific directory globs

---

### 2. Mandatory README Disclaimers

Every repository published by Googlers or under Google open source that is not an official Google product MUST include the appropriate disclaimer in the root `README.md`.

#### Standard Non-Official Product Disclaimer:

```markdown
---

## Disclaimer

This is not an officially supported Google product.
```

#### Community / Experimental Port Disclaimer:

```markdown
---

## Disclaimer

This is not an officially supported Google product. It is a community-driven, experimental port created for educational and development purposes.
```

---

## 📋 Pre-Release Compliance Checklist

Before publishing or tagging any public open-source repository, verify:

1. **License Header Coverage**:
   - Run `addlicense -check` across all code files (`.go`, `.py`, `.ts`, `.js`, `.rs`, `.c`, `.cpp`, `.sh`, `.proto`).
   - Ensure generated files (e.g. `*.pb.go`) or third-party code in `vendor/` or `third_party/` are properly ignored or attributed.
2. **Root `LICENSE` File**:
   - Ensure an unmodified copy of the chosen license (e.g. Apache 2.0) exists at the repository root.
3. **Non-Official Product Disclaimer**:
   - Present at the bottom of root `README.md`.
4. **Zero Internal Contamination**:
   - No internal links, internal issue trackers, intranet shortcuts, corporate credentials, or non-public project codenames.

---

## 📚 References & Scripts

- [License Header Variations](references/license-headers.md): Full syntax for Apache 2.0, MIT, and BSD across languages.
- [Disclaimer Variations](references/disclaimers.md): Specific disclaimer templates for samples, tools, and demos.
- [Automated Helper Script](scripts/apply-license.sh): Bundled shell script to install `addlicense` and apply headers.
