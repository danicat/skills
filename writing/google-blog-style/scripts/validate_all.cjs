#!/usr/bin/env node
/**
 * Copyright 2026 Google LLC
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


const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const draftPath = process.argv[2];

if (!draftPath) {
  console.error("Usage: node scripts/validate_all.cjs <path-to-draft>");
  process.exit(1);
}

const resolvedPath = path.resolve(draftPath);
if (!fs.existsSync(resolvedPath)) {
  console.error(`Error: File not found: ${resolvedPath}`);
  process.exit(1);
}

console.log(`# Validation Report for ${path.basename(draftPath)}\n`);
let hasErrors = false;

// 1. Lint Style
console.log(`## Style Linting (Vale)`);
try {
  const lintScript = path.join(__dirname, 'lint_style.cjs');
  if (fs.existsSync(lintScript)) {
    const lintOutput = execSync(`node "${lintScript}" "${resolvedPath}"`, { encoding: 'utf-8' });
    console.log(lintOutput);
  } else {
    console.log("lint_style.cjs script not found. Skipping.");
  }
} catch (e) {
  console.log(e.stdout || e.message);
  hasErrors = true;
}

// 2. Fog Index
console.log(`\n## Readability (Fog Index)`);
try {
  const fogScript = path.join(__dirname, 'fog.cjs');
  if (fs.existsSync(fogScript)) {
    const fogOutput = execSync(`node "${fogScript}" "${resolvedPath}"`, { encoding: 'utf-8' });
    console.log(fogOutput);
  } else {
    console.log("fog.cjs script not found. Skipping.");
  }
} catch (e) {
  console.log(e.stdout || e.message);
  hasErrors = true;
}

// 3. Legal/Sanitization
console.log(`\n## Legal & Sanitization Checks`);
try {
  const sanitizeScript = path.join(__dirname, 'sanitize_blog.cjs');
  if (fs.existsSync(sanitizeScript)) {
    const sanitizeOutput = execSync(`node "${sanitizeScript}" "${resolvedPath}"`, { encoding: 'utf-8' });
    console.log(sanitizeOutput);
  } else {
    console.log("sanitize_blog.cjs script not found. Skipping.");
  }
} catch (e) {
  console.log(e.stdout || e.message);
  hasErrors = true;
}

if (hasErrors) {
  console.log("\n**Validation failed with errors.** Please fix the issues above.");
  process.exit(1);
} else {
  console.log("\n**Validation passed successfully!**");
}
