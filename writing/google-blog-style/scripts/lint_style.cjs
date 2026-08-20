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
  console.error("Usage: node scripts/lint_style.cjs <path-to-draft>");
  process.exit(1);
}

const resolvedPath = path.resolve(draftPath);
if (!fs.existsSync(resolvedPath)) {
  console.error(`Error: File not found: ${resolvedPath}`);
  process.exit(1);
}

try {
  // Check if vale is installed
  try {
    execSync('vale -v', { stdio: 'ignore' });
  } catch (e) {
    console.error("Warning: 'vale' CLI is not installed or not in PATH.");
    console.log("Alternatively, use the speedgrapher MCP server if available.");
    process.exit(0);
  }

  console.log(`Running Vale on ${resolvedPath}...`);
  const output = execSync(`vale --output=line "${resolvedPath}"`, { encoding: 'utf-8' });
  console.log(output);
  console.log("Linting complete.");
} catch (error) {
  const errMsg = (error.stdout || '') + (error.stderr || '') + (error.message || '');
  if (errMsg.includes('no config file found') || errMsg.includes('.vale.ini not found')) {
    console.warn("Warning: Vale is installed but no local '.vale.ini' configuration file was found.");
    console.log("To use Vale, configure a '.vale.ini' file in your workspace root.");
    console.log("Alternatively, use the speedgrapher MCP server if available.");
    process.exit(0);
  }
  if (error.stdout) {
    console.log(error.stdout);
  }
  console.error("Linting found style violations. Please review.");
  process.exit(1);
}
