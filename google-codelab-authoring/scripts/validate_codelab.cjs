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

  // 2. Check Title (H1) Multiplicity
  const h1Matches = content.match(/^#\s+.+/gm);
  if (!h1Matches || h1Matches.length === 0) {
    errors.push('STRUCTURE: Missing Main Title (Heading 1)');
  } else if (h1Matches.length > 1) {
    errors.push(`STRUCTURE: Found ${h1Matches.length} H1 headers. Codelabs must have exactly ONE main title (#). Step titles must use H2 (##).`);
  }

  // 3. Check Steps (H2) and Step Durations
  const h2Matches = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('## ')) {
      h2Matches.push({ title: line.substring(3), lineNum: i + 1 });
      
      // Step durations check: look at the next lines (allow up to 2 lines down for blank space)
      let foundDuration = false;
      for (let j = 1; j <= 2; j++) {
        if (i + j < lines.length) {
          const nextLine = lines[i + j].trim();
          if (/^Duration:\s*\d+(:\d+)?$/i.test(nextLine)) {
            foundDuration = true;
            break;
          }
        }
      }
      if (!foundDuration) {
        errors.push(`STRUCTURE: Step "${line.substring(3)}" at line ${i + 1} is missing a valid 'Duration: MM:SS' statement immediately following the step header.`);
      }
    }
  }
  
  if (h2Matches.length === 0) {
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
