#!/usr/bin/env bash
# Copyright 2026 Google LLC
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

TARGET_DIR="${1:-.}"
HOLDER="${2:-Google LLC}"
LICENSE_TYPE="${3:-apache}"

# Ensure addlicense is installed
if ! command -v addlicense &>/dev/null; then
    GOPATH_BIN="$(go env GOPATH)/bin"
    if [ -f "${GOPATH_BIN}/addlicense" ]; then
        ADDLICENSE_CMD="${GOPATH_BIN}/addlicense"
    else
        echo "Installing github.com/google/addlicense@latest..."
        go install github.com/google/addlicense@latest
        ADDLICENSE_CMD="$(go env GOPATH)/bin/addlicense"
    fi
else
    ADDLICENSE_CMD="addlicense"
fi

echo "Applying ${LICENSE_TYPE} license headers with holder '${HOLDER}' in '${TARGET_DIR}'..."
"${ADDLICENSE_CMD}" -c "${HOLDER}" -l "${LICENSE_TYPE}" "${TARGET_DIR}"
echo "✅ License headers successfully applied."
