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
import os

def test_banana_help():
    script_path = os.path.join(os.path.dirname(__file__), "banana.py")
    try:
        cmd = ["uv", "run", script_path, "--help"] if os.system("which uv > /dev/null 2>&1") == 0 else [sys.executable, script_path, "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if "-p PROMPT" in result.stdout or "--prompt PROMPT" in result.stdout:
            print("Test passed: --help output contains expected arguments.")
        else:
            print("Test failed: --help output is missing arguments.")
            print(result.stdout)
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("Test failed: script execution failed.")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    test_banana_help()
