#!/usr/bin/env bash
# Copyright 2026 Daniela Petruzalek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: apply-license.sh [OPTIONS] [TARGET...]

Apply or verify source code license headers using github.com/google/addlicense.

Options:
  -h, --help                Show this help message and exit
      --check               Verify license headers without modifying files
  -c, --holder NAME         Copyright holder (default: "Google LLC")
                            Use "Google LLC" for corporate Google OSS repos, or
                            "<Author Name>" for IARC-approved personal repos
  -l, --license TYPE        License type: apache, bsd, mit, mpl (default: "apache")
  -y, --year YEAR           Copyright year or range passed to addlicense -y
  -s, --spdx-only           Emit SPDX short-form identifiers only (-s=only)
  -i, --ignore GLOB         Additional glob pattern to ignore (repeatable)
      --no-default-ignores  Do not add built-in vendor/build ignore globs

Examples:
  apply-license.sh -c "Google LLC" .
  apply-license.sh -c "Jane Doe" -l apache src/
  apply-license.sh --check -c "Google LLC" .
EOF
}

fail() {
    echo "Error: $*" >&2
    exit 1
}

require_arg() {
    if [[ $# -lt 2 || -z "$2" ]]; then
        echo "Error: option '$1' requires a non-empty value." >&2
        exit 2
    fi
}

resolve_addlicense() {
    if command -v addlicense >/dev/null 2>&1; then
        command -v addlicense
        return 0
    fi

    if ! command -v go >/dev/null 2>&1; then
        fail "neither 'addlicense' nor 'go' was found in PATH. Install Go and run: go install github.com/google/addlicense@latest"
    fi

    local go_bin
    go_bin="$(go env GOBIN)"
    if [[ -z "${go_bin}" ]]; then
        go_bin="$(go env GOPATH)/bin"
    fi

    if [[ -x "${go_bin}/addlicense" ]]; then
        printf '%s\n' "${go_bin}/addlicense"
        return 0
    fi

    echo "Installing github.com/google/addlicense@latest into ${go_bin}..." >&2
    go install github.com/google/addlicense@latest >&2

    if [[ ! -x "${go_bin}/addlicense" ]]; then
        fail "addlicense install succeeded, but executable was not found at ${go_bin}/addlicense"
    fi
    printf '%s\n' "${go_bin}/addlicense"
}

HOLDER="Google LLC"
LICENSE_TYPE="apache"
YEAR=""
CHECK_ONLY=0
SPDX_ONLY=0
USE_DEFAULT_IGNORES=1
CUSTOM_IGNORES=()
TARGETS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --check)
            CHECK_ONLY=1
            shift
            ;;
        -c|--holder)
            require_arg "$@"
            HOLDER="$2"
            shift 2
            ;;
        -l|--license)
            require_arg "$@"
            LICENSE_TYPE="$2"
            shift 2
            ;;
        -y|--year)
            require_arg "$@"
            YEAR="$2"
            shift 2
            ;;
        -s|--spdx-only)
            SPDX_ONLY=1
            shift
            ;;
        -i|--ignore)
            require_arg "$@"
            CUSTOM_IGNORES+=("$2")
            shift 2
            ;;
        --no-default-ignores)
            USE_DEFAULT_IGNORES=0
            shift
            ;;
        --)
            shift
            while [[ $# -gt 0 ]]; do
                TARGETS+=("$1")
                shift
            done
            ;;
        -*)
            echo "Error: unknown option '$1'. Run with --help for usage." >&2
            exit 2
            ;;
        *)
            TARGETS+=("$1")
            shift
            ;;
    esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    TARGETS=(".")
fi

for target in "${TARGETS[@]}"; do
    if [[ ! -e "${target}" ]]; then
        fail "target path does not exist: ${target}"
    fi
done

ADDLICENSE_CMD="$(resolve_addlicense)"

ARGS=(-c "${HOLDER}" -l "${LICENSE_TYPE}")

if [[ ${CHECK_ONLY} -eq 1 ]]; then
    ARGS+=(-check)
fi

if [[ -n "${YEAR}" ]]; then
    ARGS+=(-y "${YEAR}")
fi

if [[ ${SPDX_ONLY} -eq 1 ]]; then
    ARGS+=(-s=only)
fi

if [[ ${USE_DEFAULT_IGNORES} -eq 1 ]]; then
    DEFAULT_IGNORES=(
        ".git/**"
        "node_modules/**"
        "**/node_modules/**"
        ".venv/**"
        "**/.venv/**"
        "venv/**"
        "**/venv/**"
        "vendor/**"
        "**/vendor/**"
        "third_party/**"
        "**/third_party/**"
        "dist/**"
        "**/dist/**"
        "build/**"
        "**/build/**"
        "_site/**"
        "**/_site/**"
        "*.pb.go"
        "**/*.pb.go"
    )
    for pattern in "${DEFAULT_IGNORES[@]}"; do
        ARGS+=(-ignore "${pattern}")
    done
fi

if [[ ${#CUSTOM_IGNORES[@]} -gt 0 ]]; then
    for pattern in "${CUSTOM_IGNORES[@]}"; do
        ARGS+=(-ignore "${pattern}")
    done
fi

ARGS+=("${TARGETS[@]}")

if [[ ${CHECK_ONLY} -eq 1 ]]; then
    echo "Checking ${LICENSE_TYPE} license headers (holder: '${HOLDER}') in: ${TARGETS[*]}"
else
    echo "Applying ${LICENSE_TYPE} license headers (holder: '${HOLDER}') in: ${TARGETS[*]}"
fi

"${ADDLICENSE_CMD}" "${ARGS[@]}"
