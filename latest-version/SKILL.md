---
name: latest-version
description: >
  Fetches package versions from NPM, PyPI, Go, Cargo, and RubyGems, or gets Gemini models. This tool queries registries to get stable versions and warn about deprecated, yanked, or retracted packages.
---

# Latest Software Version (latest-version)

Queries registries to find stable package versions. Do not guess versions or rely on outdated knowledge.

## How to use

### 1. Find the ecosystem
We support these registries:
* npm: Node.js/JS
* pypi: Python
* go: Go
* cargo: Rust
* gem: Ruby
* gemini: Gemini models (use 'latest', 'flash', or 'pro' as the name)

### 2. Run the command
Run this script:
```bash
node scripts/latest.js <ecosystem> <package-name>
```

### 3. Save the version
Put the returned version in your config or command.
* Example: If you get `npm: react @ 19.2.0`, update package.json with `"react": "^19.2.0"`.

## Registry URLs
* NPM: registry.npmjs.org
* PyPI: pypi.org
* Go Proxy: proxy.golang.org
* Crates.io: crates.io
* RubyGems: rubygems.org
