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

import subprocess
import sys
import json
import os

def run_cmd(args):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=False)
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return -1, "", str(e)

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."

    # 1. Run Ruff Check
    lint_code, lint_out, lint_err = run_cmd(["uv", "run", "ruff", "check", target])

    # 2. Run Ruff Format Check
    fmt_code, fmt_out, fmt_err = run_cmd(["uv", "run", "ruff", "format", "--check", target])

    # 3. Run Pytest
    test_code, test_out, test_err = run_cmd(["uv", "run", "pytest"])

    summary = {
        "success": (lint_code == 0) and (fmt_code == 0) and (test_code == 0),
        "ruff_check": {
            "passed": lint_code == 0,
            "code": lint_code,
            "errors": [line for line in lint_out.splitlines() if line] if lint_code != 0 else [],
            "error_msg": lint_err
        },
        "ruff_format": {
            "passed": fmt_code == 0,
            "code": fmt_code,
            "errors": [line for line in fmt_out.splitlines() if line] if fmt_code != 0 else [],
            "error_msg": fmt_err
        },
        "pytest": {
            "passed": test_code == 0,
            "code": test_code,
            "summary": [line for line in test_out.splitlines() if "failed" in line or "passed in" in line or "error" in line.lower()][-3:] if test_code != 0 else ["All tests passed"],
            "error_msg": test_err if test_code != 0 and not test_out else ""
        }
    }

    print(json.dumps(summary, indent=2))
    if not summary["success"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
