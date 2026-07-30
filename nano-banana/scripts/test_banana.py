import subprocess
import sys
import os

def test_banana_help():
    script_path = os.path.join(os.path.dirname(__file__), "banana.py")
    try:
        result = subprocess.run([sys.executable, script_path, "--help"], capture_output=True, text=True, check=True)
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
