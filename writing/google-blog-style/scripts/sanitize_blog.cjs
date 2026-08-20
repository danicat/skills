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

const fs = require('fs');
const path = require('path');

const filePath = process.argv[2];

if (!filePath) {
  console.error('Usage: node sanitize_blog.cjs <path-to-blog.md>');
  process.exit(1);
}

try {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  const warnings = [];

  // Structure Checks (Simple regex)
  const hasHero = /hero_image:|!\[.*\]\(.*(png|jpg|gif|mp4).*\)/i.test(content);
  if (!hasHero) {
    warnings.push('Structure: Missing Hero Image. Add a `hero_image` field or an image at the top.');
  }

  const hasCTA = /call to action|learn more|try it out|get started/i.test(content);
  if (!hasCTA) {
    warnings.push('Structure: Weak or Missing Call to Action (CTA). Ensure you link to docs/codelabs at the end.');
  }

  // Regex patterns for potential sensitive data AND legal pitfalls
  const patterns = [
    // Security & Secrets
    { name: 'Google API Key', regex: /AIza[0-9A-Za-z-_]{35}/, suggestion: 'Replace with a placeholder (e.g., "YOUR_API_KEY")' },
    { name: 'Hardcoded Home Directory', regex: /(\/Users\/|\/home\/|[a-zA-Z]:[\\\/](Users|Documents|Projects))[a-zA-Z0-9._-]+/, suggestion: 'Use relative paths or placeholders' },
    { name: 'Internal Corporate Tooling/Teams', regex: /\b(corp\.google\.com|google3|xid\/|critique\/|googleplex|buganizer|DSS|DevRel\s+Influencers)\b/i, suggestion: 'Remove internal infrastructure or team references.' },
    { name: 'Potential Private Project ID', regex: /[a-z0-9]+-(sandbox|dev|test)-[a-z0-9]+/, suggestion: 'Check if this is a personal project ID. Use a generic placeholder like "my-project-id".' },

    // Legal & Editorial
    { name: 'Superlative ("Best")', regex: /\b(best|simplest|easiest|unmatched)\b/i, suggestion: 'Avoid superlatives unless substantiated. Use precise language.' },
    { name: 'Absolute Guarantee', regex: /\b(guaranteed|100%|always|never|zero latency)\b/i, suggestion: 'Avoid absolutes. Use "designed for" or "helps ensure".' },
    { name: 'Unbreakable Security', regex: /\b(unbreakable|bulletproof|ironclad|hack-proof)\b/i, suggestion: 'Never imply perfect security. Use "helps secure".' },
    { name: 'Future Promise', regex: /\b(coming soon|roadmap|future release)\b/i, suggestion: 'Do not discuss future features/roadmaps.' },
    { name: 'Invalid Domain', regex: /https?:\/\/(?!example\.(com|org|net)|google\.com|googleapis\.com|github\.com|developers\.googleblog\.com)[a-z0-9-]+\.[a-z]+/i, suggestion: 'Use only example.com/org/net for fictional domains (or approved real ones).' }
  ];

  lines.forEach((line, index) => {
    patterns.forEach(p => {
      if (p.regex.test(line)) {
        if (p.name === 'Superlative ("Best")' && line.toLowerCase().includes('best practice')) return;
        warnings.push(`Line ${index + 1}: Possible ${p.name} detected. ${p.suggestion}\n   Match: "${line.trim()}"`);
      }
    });
  });

  if (warnings.length > 0) {
    console.log('⚠️  Sanitization/Legal Warnings Found:');
    warnings.forEach(w => console.log(`  - ${w}`));
    console.log('\nPlease review these lines manually. If they are false positives, you can ignore them.');
    process.exit(1);
  } else {
    console.log('✅ Sanitization & Legal Check Passed: No obvious issues found.');
  }

} catch (err) {
  console.error(`Error reading file: ${err.message}`);
  process.exit(1);
}
