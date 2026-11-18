/**
 * Copyright 2026 Daniela Petruzalek
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import test from 'node:test';
import assert from 'node:assert/strict';

import {
  classifyTier,
  computeFreshnessScore,
  countSubstantiveLinesFromDiff,
} from './update_freshness.mjs';

test('computeFreshnessScore enforces 30-day grace window and 90-day half-life', () => {
  const cases = [
    [-5, 100],
    [0, 100],
    [15, 100],
    [30, 100],
    [60, 79],
    [90, 63],
    [120, 50],
    [210, 25],
    [365, 8],
  ];

  for (const [ageDays, expectedScore] of cases) {
    assert.equal(
      computeFreshnessScore(ageDays),
      expectedScore,
      `Expected ${expectedScore} for ageDays=${ageDays}`
    );
  }
});

test('classifyTier maps numeric score brackets to engineering tiers', () => {
  assert.deepEqual(classifyTier(100), { tier: 'current', label: 'Current' });
  assert.deepEqual(classifyTier(85), { tier: 'current', label: 'Current' });
  assert.deepEqual(classifyTier(84), { tier: 'active', label: 'Active' });
  assert.deepEqual(classifyTier(60), { tier: 'active', label: 'Active' });
  assert.deepEqual(classifyTier(59), { tier: 'aging', label: 'Aging' });
  assert.deepEqual(classifyTier(35), { tier: 'aging', label: 'Aging' });
  assert.deepEqual(classifyTier(34), { tier: 'outdated', label: 'Outdated' });
  assert.deepEqual(classifyTier(0), { tier: 'outdated', label: 'Outdated' });
});

test('countSubstantiveLinesFromDiff ignores license headers and frontmatter noise', () => {
  const metadataOnlyDiff = [
    'diff --git a/coding/example/SKILL.md b/coding/example/SKILL.md',
    '--- a/coding/example/SKILL.md',
    '+++ b/coding/example/SKILL.md',
    '@@ -1,10 +1,11 @@',
    '---',
    '-version: "0.1.0"',
    '+version: "0.1.1"',
    '-tags: "go, testing"',
    '+tags: "go, tests"',
    '+catalog: https://skills.danicat.dev',
    '+# Copyright 2026 Daniela Petruzalek',
    '+# Licensed under the Apache License, Version 2.0',
    '+',
  ].join('\n');

  assert.equal(countSubstantiveLinesFromDiff(metadataOnlyDiff), 0);

  const realDiff = [
    'diff --git a/coding/example/scripts/helper.py b/coding/example/scripts/helper.py',
    '--- a/coding/example/scripts/helper.py',
    '+++ b/coding/example/scripts/helper.py',
    '@@ -10,2 +10,5 @@',
    '-    return old_value()',
    '+    # Validate input strictly before execution',
    '+    if not payload:',
    '+        raise ValueError("empty payload")',
    '+    return new_value(payload)',
  ].join('\n');

  assert.equal(countSubstantiveLinesFromDiff(realDiff), 5);
});
