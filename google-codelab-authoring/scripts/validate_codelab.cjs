#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const filePath = process.argv[2];

if (!filePath) {
  console.error('Usage: node validate_codelab.cjs <path-to-lab.md>');
  process.exit(1);
}

try {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  const errors = [];

  // 1. Check Metadata (Frontmatter)
  if (!content.startsWith('---')) {
    errors.push('CRITICAL: File must start with YAML frontmatter (---)');
  } else {
    const endFrontmatter = content.indexOf('---', 3);
    if (endFrontmatter === -1) {
      errors.push('CRITICAL: YAML frontmatter must be closed with ---');
    } else {
      const frontmatter = content.substring(3, endFrontmatter);
      const requiredKeys = ['id', 'description', 'authors', 'layout'];
      requiredKeys.forEach(key => {
        if (!frontmatter.includes(`${key}:`)) {
          errors.push(`METADATA: Missing required key: '${key}'`);
        }
      });
    }
  }

  // 2. Check Title (H1)
  const h1Match = content.match(/^#\s+(.+)/m);
  if (!h1Match) {
    errors.push('STRUCTURE: Missing Main Title (Heading 1)');
  }

  // 3. Check Steps (H2)
  const h2Matches = content.match(/^##\s+(.+)/gm);
  if (!h2Matches || h2Matches.length === 0) {
    errors.push('STRUCTURE: No steps found (Heading 2). A codelab must have at least one step.');
  }

  // 4. Check Info Boxes
  const invalidAsides = content.match(/>\s*aside\s+(?!positive|negative)\w+/g);
  if (invalidAsides) {
    invalidAsides.forEach(match => {
      errors.push(`SYNTAX: Invalid aside type: '${match}'. Use 'positive' or 'negative'.`);
    });
  }

  // Output results
  if (errors.length > 0) {
    console.log('❌ Validation Failed:');
    errors.forEach(err => console.log(`  - ${err}`));
    process.exit(1);
  } else {
    console.log('✅ Validation Passed: Codelab structure looks good!');
  }

} catch (err) {
  console.error(`Error reading file: ${err.message}`);
  process.exit(1);
}
