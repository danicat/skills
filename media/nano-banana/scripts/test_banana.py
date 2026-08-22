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
    cmd = ["uv", "run", script_path, "--help"] if os.system("which uv > /dev/null 2>&1") == 0 else [sys.executable, script_path, "--help"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        assert "--prompt" in result.stdout or "-p" in result.stdout
        assert "--aspect-ratio" in result.stdout or "-a" in result.stdout
        assert "--resolution" in result.stdout or "-r" in result.stdout
        assert "--thinking-level" in result.stdout
        assert "--search" in result.stdout
        assert "--image-search" in result.stdout
        assert "--api" in result.stdout
        print("Test passed: banana.py --help includes all expected flags.")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

def test_capability_validation():
    script_path = os.path.join(os.path.dirname(__file__), "banana.py")
    cmd_base = ["uv", "run", script_path] if os.system("which uv > /dev/null 2>&1") == 0 else [sys.executable, script_path]

    # Test 1: Nano Banana 2 Lite rejecting 4K resolution
    res = subprocess.run(cmd_base + ["-p", "test", "-f", "out.png", "-m", "nano-banana-2-lite", "-r", "4K"], capture_output=True, text=True)
    assert res.returncode != 0
    assert "Resolution '4K' is not supported by nano-banana-2-lite" in res.stderr
    print("Test passed: 4K rejected on nano-banana-2-lite.")

    # Test 2: Search grounding rejected on nano-banana-2-lite
    res = subprocess.run(cmd_base + ["-p", "test", "-f", "out.png", "-m", "nano-banana-2-lite", "--search"], capture_output=True, text=True)
    assert res.returncode != 0
    assert "Search grounding is not supported by nano-banana-2-lite" in res.stderr
    print("Test passed: Search grounding rejected on nano-banana-2-lite.")

    # Test 3: Thinking level rejected on nano-banana
    res = subprocess.run(cmd_base + ["-p", "test", "-f", "out.png", "-m", "nano-banana", "--thinking-level", "high"], capture_output=True, text=True)
    assert res.returncode != 0
    assert "Thinking mode is not supported by 'nano-banana'" in res.stderr
    print("Test passed: Thinking level rejected on nano-banana.")

if __name__ == "__main__":
    test_banana_help()
    test_capability_validation()
    print("All banana CLI tests passed successfully!")
