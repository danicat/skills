#!/usr/bin/env python3
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

"""
Centralized Test Suite Runner for All Analytics Skills:
- writing/buffer-analytics
- writing/google-analytics
- writing/search-analytics

Validates:
1. SQLite Database schemas, DDL scripts, indexes, and views.
2. In-memory data fixtures and relational integrity.
3. Every SQL query used as an example across SKILL.md and references/queries.md.
4. Pre-packaged CLI analytical reports across all engines.
5. Dynamic extraction and validation of markdown SQL code blocks.
6. CLI argument parsers and command interfaces.
"""

import io
import os
import sys
import time
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


def run_all_analytics_tests() -> int:
    print("=" * 78)
    print("  ANALYTICS SKILLS COMPREHENSIVE TEST SUITE")
    print("=" * 78)
    print(f"Repository Root: {REPO_ROOT}\n")

    test_targets = [
        ("Buffer Analytics", os.path.join(REPO_ROOT, "writing", "buffer-analytics", "scripts"), "test_buffer_analytics.py"),
        ("Google Analytics 4", os.path.join(REPO_ROOT, "writing", "google-analytics", "scripts"), "test_google_analytics.py"),
        ("Search Analytics (GSC)", os.path.join(REPO_ROOT, "writing", "search-analytics", "scripts"), "test_search_analytics.py"),
    ]

    total_suites = 0
    total_tests = 0
    total_failures = 0
    total_errors = 0
    start_time = time.time()

    results_summary = []

    for name, directory, filename in test_targets:
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            continue

        sys.path.insert(0, directory)
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=directory, pattern=filename)

        stream = io.StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        result = runner.run(suite)

        suite_count = suite.countTestCases()
        fail_count = len(result.failures)
        err_count = len(result.errors)

        total_suites += 1
        total_tests += suite_count
        total_failures += fail_count
        total_errors += err_count

        status_str = "PASSED" if (fail_count == 0 and err_count == 0) else "FAILED"
        icon = "✅" if status_str == "PASSED" else "❌"

        results_summary.append({
            "name": name,
            "tests": suite_count,
            "failures": fail_count,
            "errors": err_count,
            "status": status_str,
            "icon": icon,
            "output": stream.getvalue(),
        })

    elapsed = time.time() - start_time

    # Print summary table
    print(f"{'Skill Name':<28} | {'Tests':<8} | {'Failures':<10} | {'Errors':<8} | {'Status':<10}")
    print("-" * 78)
    for res in results_summary:
        print(f"{res['icon']} {res['name']:<25} | {res['tests']:<8} | {res['failures']:<10} | {res['errors']:<8} | {res['status']:<10}")
    print("-" * 78)
    print(f"Total Tests Executed: {total_tests} across {total_suites} skills in {elapsed:.3f}s")
    print(f"Total Failures: {total_failures}, Total Errors: {total_errors}\n")

    if total_failures > 0 or total_errors > 0:
        print("❌ Test failures detected:")
        for res in results_summary:
            if res["failures"] > 0 or res["errors"] > 0:
                print(f"\n--- Output for {res['name']} ---")
                print(res["output"])
        return 1

    print("🎉 All analytics database schemas, analytical views, and example queries validated successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(run_all_analytics_tests())
