#!/usr/bin/env node

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
