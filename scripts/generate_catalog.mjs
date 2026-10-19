#!/usr/bin/env node
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

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');

const SCHEMA_URI = 'https://schemas.agentskills.io/discovery/0.2.0/schema.json';
const BASE_URL = 'https://skills.danicat.dev';
const REPO_URL = 'https://github.com/danicat/skills';

const CATEGORY_ORDER = [
  { id: 'agents', emoji: '🤖' },
  { id: 'analytics', emoji: '📊' },
  { id: 'game-dev', emoji: '🕹️' },
  { id: 'media', emoji: '🎨' },
  { id: 'coding', emoji: '💻' },
  { id: 'writing', emoji: '✍️' },
];

function readRequiredJson(relPath) {
  const fullPath = path.join(ROOT_DIR, relPath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`[Fail-Fast] Required data file missing: ${relPath}`);
  }
  return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
}

function parseFrontmatterStrict(rawContent, relPath) {
  const match = rawContent.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) {
    throw new Error(`[Fail-Fast] Missing YAML frontmatter in ${relPath}`);
  }

  const rawYaml = match[1];
  const data = {};
  const lines = rawYaml.split(/\r?\n/);
  let currentKey = null;
  let inMetadata = false;
  const metadataObj = {};

  for (const line of lines) {
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
        if (
          (mVal.startsWith('"') && mVal.endsWith('"')) ||
          (mVal.startsWith("'") && mVal.endsWith("'"))
        ) {
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
        if (val === '>' || val === '|' || val === '>-' || val === '|-') {
          currentKey = key;
          data[key] = '';
          continue;
        }
        if (
          (val.startsWith('"') && val.endsWith('"')) ||
          (val.startsWith("'") && val.endsWith("'"))
        ) {
          val = val.slice(1, -1);
        }
        data[key] = val;
        currentKey = null;
      } else if (currentKey) {
        data[currentKey] = (data[currentKey] ? `${data[currentKey]} ` : '') + trimmed;
      }
    }
  }

  data.metadata = metadataObj;

  if (!data.name || !data.description || !data.license) {
    throw new Error(`[Fail-Fast] Missing required top-level frontmatter fields in ${relPath}`);
  }
  if (!data.metadata.category || !data.metadata.tags || !data.metadata.author || !data.metadata.version) {
    throw new Error(`[Fail-Fast] Missing required metadata fields in ${relPath}`);
  }

  return data;
}

export function generateCatalog() {
  const translations = readRequiredJson('data/translations.json');
  const freshnessMap = readRequiredJson('data/freshness.json');
  const graveyard = readRequiredJson('data/graveyard.json');

  const enCategories = translations?.en?.categories;
  if (!enCategories) {
    throw new Error('[Fail-Fast] Missing en.categories in data/translations.json');
  }

  const categories = [];
  const skills = [];

  for (const catDef of CATEGORY_ORDER) {
    const catTrans = enCategories[catDef.id];
    if (!catTrans || !catTrans.name || !catTrans.description) {
      throw new Error(`[Fail-Fast] Missing category translation metadata for "${catDef.id}"`);
    }

    categories.push({
      id: catDef.id,
      name: catTrans.name,
      emoji: catDef.emoji,
      description: catTrans.description,
    });

    const catDir = path.join(ROOT_DIR, catDef.id);
    if (!fs.existsSync(catDir)) {
      throw new Error(`[Fail-Fast] Category directory does not exist: ${catDef.id}`);
    }

    const skillFolders = fs
      .readdirSync(catDir, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name)
      .sort();

    for (const folder of skillFolders) {
      const relSkillPath = `${catDef.id}/${folder}/SKILL.md`;
      const fullSkillPath = path.join(ROOT_DIR, relSkillPath);
      if (!fs.existsSync(fullSkillPath)) {
        continue;
      }

      const rawBytes = fs.readFileSync(fullSkillPath);
      const rawText = rawBytes.toString('utf8');
      const sha256Hex = crypto.createHash('sha256').update(rawBytes).digest('hex');
      const fm = parseFrontmatterStrict(rawText, relSkillPath);

      const tags = fm.metadata.tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);

      const skillId = fm.name.toLowerCase();
      const f = freshnessMap[skillId];
      if (!f) {
        throw new Error(
          `[Fail-Fast] Skill "${skillId}" is missing from data/freshness.json. Run: node scripts/update_freshness.mjs`
        );
      }
      const freshnessScore = f.isUnproven ? null : Number(f.score);
      const freshnessTier = f.tier;
      const freshnessEmoji = f.tierEmoji;
      const lastCommitAt = f.lastCommitAt;

      skills.push({
        name: fm.name,
        type: 'skill-md',
        description: fm.description.trim(),
        category: fm.metadata.category,
        tags,
        author: fm.metadata.author,
        version: fm.metadata.version,
        license: fm.license,
        url: `${BASE_URL}/${catDef.id}/${folder}/SKILL.md`,
        digest: `sha256:${sha256Hex}`,
        freshnessScore,
        freshnessTier,
        freshnessEmoji,
        lastCommitAt,
      });
    }
  }

  const updatedAt = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');

  const catalogManifest = {
    $schema: SCHEMA_URI,
    name: 'danicat/skills',
    title: 'Agent Skills',
    url: BASE_URL,
    repository: REPO_URL,
    totalSkills: skills.length,
    updatedAt,
    categories,
    skills,
    graveyard,
  };

  const catalogJson = JSON.stringify(catalogManifest, null, 2) + '\n';

  // Build llms.txt
  let llmsTxt = `# danicat/skills\n\n> A curated collection of specialized Agent Skills for coding, game development, generative media, writing, and standards.\n\n`;
  for (const cat of categories) {
    const catSkills = skills.filter((s) => s.category === cat.id);
    if (catSkills.length === 0) continue;
    llmsTxt += `## ${cat.name}\n\n`;
    for (const s of catSkills) {
      llmsTxt += `- [${s.name}](${s.url}): ${s.description}\n`;
    }
    llmsTxt += `\n`;
  }
  llmsTxt += `## Optional\n\n`;
  llmsTxt += `- [Full Instructions Catalog](${BASE_URL}/llms-full.txt): Complete bundle of all ${skills.length} skill instructions in a single file for large-context models.\n`;
  llmsTxt += `- [Catalog Manifest](${BASE_URL}/catalog.json): Machine-readable catalog manifest with metadata, tags, and digests.\n`;
  llmsTxt += `- [Agent Skills Discovery Index](${BASE_URL}/.well-known/agent-skills/index.json): RFC v0.2.0 well-known discovery index with SHA-256 digests.\n`;

  // Write root artifacts
  const rootCatalogPath = path.join(ROOT_DIR, 'catalog.json');
  const rootLlmsPath = path.join(ROOT_DIR, 'llms.txt');
  fs.writeFileSync(rootCatalogPath, catalogJson, 'utf8');
  fs.writeFileSync(rootLlmsPath, llmsTxt, 'utf8');

  // Sync to static/ and static/.well-known/agent-skills/index.json
  const staticCatalogPath = path.join(ROOT_DIR, 'static', 'catalog.json');
  const staticLlmsPath = path.join(ROOT_DIR, 'static', 'llms.txt');
  const wellKnownIndexPath = path.join(ROOT_DIR, 'static', '.well-known', 'agent-skills', 'index.json');

  fs.mkdirSync(path.dirname(staticCatalogPath), { recursive: true });
  fs.mkdirSync(path.dirname(wellKnownIndexPath), { recursive: true });

  fs.writeFileSync(staticCatalogPath, catalogJson, 'utf8');
  fs.writeFileSync(staticLlmsPath, llmsTxt, 'utf8');
  fs.writeFileSync(wellKnownIndexPath, catalogJson, 'utf8');

  console.log(
    `✅ Generated catalog (${skills.length} active skills across ${categories.length} categories) -> catalog.json, static/catalog.json, static/.well-known/agent-skills/index.json, llms.txt, static/llms.txt`
  );

  return catalogManifest;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  generateCatalog();
}
