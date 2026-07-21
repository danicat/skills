#!/usr/bin/env node

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

