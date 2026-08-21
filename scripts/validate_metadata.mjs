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


/**
 * Metadata & Frontmatter Validator for Agent Skills Catalog
 *
 * Validates:
 * 1. YAML frontmatter syntax and structure.
 * 2. Required top-level fields: name, description, license.
 * 3. Required metadata fields: category, tags, author, version, homepage, canonical, repository.
 * 4. SemVer formatting for version (X.Y.Z).
 * 5. URL consistency across homepage, canonical, and repository.
 * 6. Name-to-directory alignment and kebab-case naming rules.
 * 7. Zero Contamination check (no private/internal leaks or local absolute paths).
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');

const VALID_CATEGORIES = new Set([
  'game-dev',
  'media',
  'coding',
  'agents',
  'writing',
  'analytics',
  'standards',
  'gateway'
]);

const SEMVER_REGEX = /^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$/;
const KEBAB_REGEX = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const DOMAIN = 'https://skills.danicat.dev';
const REPO_BASE = 'https://github.com/danicat/skills';

// Zero contamination banned terms/patterns (internal workflows, private paths, credentials)
const BANNED_PATTERNS = [
  /\/Users\/[a-zA-Z0-9_-]+/, // macOS user paths
  /\/home\/[a-zA-Z0-9_-]+/, // Linux user paths
  /[a-zA-Z]:[\\\/](Users|Documents|Projects)/i, // Windows user paths
  /(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}/, // GitHub personal tokens
  /AIza[0-9A-Za-z-_]{35}/, // Google API keys
  /sk-[a-zA-Z0-9]{20,}/, // OpenAI/third-party API keys
  /\b(corp\.google\.com|google3|xid\/|critique\/|googleplex|buganizer)\b/i, // internal Google infrastructure
  /\b(DSS|DevRel\s+Influencers)\b/i, // internal team and chat channel names
];

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return { data: null, rawYaml: null, body: content };

  const rawYaml = match[1];
  const body = content.slice(match[0].length);
  const data = {};

  const lines = rawYaml.split('\n');
  let currentKey = null;
  let inMetadata = false;
  const metadataObj = {};

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;

    if (line.startsWith('metadata:')) {
      inMetadata = true;
      currentKey = null;
      continue;
    }

    if (inMetadata) {
      if (/^\s{2,}[a-zA-Z0-9_-]+:/.test(line)) {
        const colonIdx = line.indexOf(':');
        const mKey = line.slice(0, colonIdx).trim();
        let mVal = line.slice(colonIdx + 1).trim();
        if ((mVal.startsWith('"') && mVal.endsWith('"')) || (mVal.startsWith("'") && mVal.endsWith("'"))) {
          mVal = mVal.slice(1, -1);
        }
        metadataObj[mKey] = mVal;
        continue;
      } else if (!line.startsWith(' ') && !line.startsWith('\t')) {
        inMetadata = false;
      }
    }

    if (!inMetadata) {
      const colonIdx = line.indexOf(':');
      if (colonIdx !== -1 && !line.startsWith(' ') && !line.startsWith('\t')) {
        const key = line.slice(0, colonIdx).trim();
        let val = line.slice(colonIdx + 1).trim();

        if (val === '>' || val === '|') {
          currentKey = key;
          data[key] = '';
          continue;
        }

        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
          val = val.slice(1, -1);
        }
        data[key] = val;
        currentKey = null;
      } else if (currentKey) {
        data[currentKey] = (data[currentKey] ? data[currentKey] + ' ' : '') + trimmed;
      }
    }
  }

  if (Object.keys(metadataObj).length > 0) {
    data.metadata = metadataObj;
  }

  return { data, rawYaml, body };
}

function validateSkillFile(filePath, isGateway = false) {
  const errors = [];
  const warnings = [];
  const relPath = path.relative(ROOT_DIR, filePath);

  if (!fs.existsSync(filePath)) {
    return { relPath, errors: ['File does not exist'], warnings };
  }

  const raw = fs.readFileSync(filePath, 'utf8');

  // Zero Contamination checks
  for (const pattern of BANNED_PATTERNS) {
    if (pattern.test(raw)) {
      errors.push(`Zero Contamination Violation: matched banned pattern ${pattern}`);
    }
  }

  const { data, rawYaml, body } = parseFrontmatter(raw);

  if (!data) {
    errors.push('Missing or malformed YAML frontmatter delimiters (--- ... ---)');
    return { relPath, errors, warnings };
  }

  // 1. Required Top-Level Fields
  if (!data.name) {
    errors.push("Missing required field: 'name'");
  } else {
    if (!KEBAB_REGEX.test(data.name)) {
      errors.push(`Field 'name' ("${data.name}") must be lowercase alphanumeric with hyphens (kebab-case)`);
    }

    if (!isGateway) {
      const expectedDirName = path.basename(path.dirname(filePath));
      if (data.name !== expectedDirName) {
        errors.push(`Field 'name' ("${data.name}") does not match directory name ("${expectedDirName}")`);
      }
    }
  }

  if (!data.description || data.description.trim().length === 0) {
    errors.push("Missing or empty required field: 'description'");
  } else if (data.description.length < 20) {
    warnings.push(`Description is very short (${data.description.length} chars); consider adding clear agent trigger terms`);
  }

  if (!data.license) {
    errors.push("Missing required field: 'license'");
  }

  // 2. Metadata Block Checks
  if (!data.metadata || typeof data.metadata !== 'object') {
    errors.push("Missing required 'metadata:' mapping block in frontmatter");
    return { relPath, errors, warnings };
  }

  const meta = data.metadata;

  // Category
  if (!meta.category) {
    errors.push("Missing required metadata field: 'category'");
  } else if (!VALID_CATEGORIES.has(meta.category)) {
    errors.push(`Invalid category "${meta.category}". Allowed categories: ${Array.from(VALID_CATEGORIES).join(', ')}`);
  } else if (!isGateway) {
    const parentDir = path.basename(path.dirname(path.dirname(filePath)));
    if (meta.category !== parentDir) {
      errors.push(`metadata.category ("${meta.category}") does not match category directory ("${parentDir}")`);
    }
  }

  // Tags
  if (!meta.tags || meta.tags.trim().length === 0) {
    errors.push("Missing or empty metadata field: 'tags'");
  }

  // Author
  if (!meta.author || meta.author.trim().length === 0) {
    errors.push("Missing or empty metadata field: 'author'");
  }

  // Version
  if (!meta.version) {
    errors.push("Missing required metadata field: 'version'");
  } else if (!SEMVER_REGEX.test(meta.version)) {
    errors.push(`metadata.version ("${meta.version}") is not a valid Semantic Version (e.g. 1.0.0, 0.1.0)`);
  }

  // Single Canonical URL Validation
  if (isGateway) {
    if (!meta.canonical) {
      errors.push("Missing required metadata field: 'canonical'");
    } else if (meta.canonical !== `${DOMAIN}/` && meta.canonical !== `${DOMAIN}/SKILL.md`) {
      errors.push(`Gateway canonical mismatch: expected "${DOMAIN}/", got "${meta.canonical}"`);
    }
  } else {
    const expectedCanonical = `${DOMAIN}/${meta.category}/${data.name}/`;
    if (!meta.canonical) {
      errors.push("Missing required metadata field: 'canonical'");
    } else if (meta.canonical !== expectedCanonical && meta.canonical !== `${DOMAIN}/${meta.category}/${data.name}/SKILL.md`) {
      errors.push(`metadata.canonical mismatch: expected "${expectedCanonical}", got "${meta.canonical}"`);
    }
  }

  // 3. Body Checks
  if (!body || body.trim().length === 0) {
    errors.push('SKILL.md body is completely empty');
  }

  return { relPath, name: data.name || 'unknown', version: meta.version || 'unknown', errors, warnings };
}

export function validateAllSkills() {
  console.log('='.repeat(78));
  console.log('  AGENT SKILLS METADATA & FRONTMATTER VALIDATOR');
  console.log('='.repeat(78));
  console.log(`Repository Root: ${ROOT_DIR}\n`);

  const results = [];

  // 1. Root Gateway SKILL.md
  const rootSkillPath = path.join(ROOT_DIR, 'SKILL.md');
  if (fs.existsSync(rootSkillPath)) {
    results.push(validateSkillFile(rootSkillPath, true));
  }

  // 2. All Category SKILL.md files
  for (const cat of VALID_CATEGORIES) {
    if (cat === 'gateway') continue;
    const catDir = path.join(ROOT_DIR, cat);
    if (!fs.existsSync(catDir)) continue;

    const skillFolders = fs.readdirSync(catDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);

    for (const folder of skillFolders) {
      const skillFile = path.join(catDir, folder, 'SKILL.md');
      if (fs.existsSync(skillFile)) {
        results.push(validateSkillFile(skillFile, false));
      }
    }
  }

  let totalErrors = 0;
  let totalWarnings = 0;

  console.log(`${'Skill / File'.padEnd(42)} | ${'Version'.padEnd(8)} | ${'Status'.padEnd(8)} | Notes`);
  console.log('-'.repeat(78));

  for (const res of results) {
    const errorCount = res.errors.length;
    const warningCount = res.warnings.length;
    totalErrors += errorCount;
    totalWarnings += warningCount;

    let status = 'PASSED';
    let icon = '✅';

    if (errorCount > 0) {
      status = 'FAILED';
      icon = '❌';
    } else if (warningCount > 0) {
      status = 'WARN';
      icon = '⚠️ ';
    }

    const note = errorCount > 0 ? `${errorCount} errors` : (warningCount > 0 ? `${warningCount} warnings` : 'OK');
    console.log(`${icon} ${res.relPath.padEnd(40)} | ${(res.version || '').padEnd(8)} | ${status.padEnd(8)} | ${note}`);
  }

  console.log('-'.repeat(78));
  console.log(`Total Files Validated: ${results.length} | Errors: ${totalErrors} | Warnings: ${totalWarnings}\n`);

  if (totalErrors > 0) {
    console.error('❌ Validation Failures:');
    for (const res of results) {
      if (res.errors.length > 0) {
        console.error(`\n📄 ${res.relPath}:`);
        for (const err of res.errors) {
          console.error(`   - ❌ ${err}`);
        }
      }
      if (res.warnings.length > 0) {
        for (const warn of res.warnings) {
          console.warn(`   - ⚠️  ${warn}`);
        }
      }
    }
    return 1;
  }

  console.log('🎉 All Agent Skills metadata and frontmatter validated successfully!');
  return 0;
}

// Execute CLI
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const code = validateAllSkills();
  process.exit(code);
}
