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
  { id: 'workflows', emoji: '🔄' },
  { id: 'traits', emoji: '🧬' },
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

function extractMarkdownBody(rawContent) {
  const norm = rawContent.replace(/\r\n/g, '\n');
  if (norm.startsWith('---\n')) {
    const trimmed = norm.slice(4);
    const parts = trimmed.split('\n---\n');
    if (parts.length > 1) {
      return parts.slice(1).join('\n---\n').trim();
    }
  }
  return norm.trim();
}

function buildRepresentativeQueries(skill) {
  const queries = [
    `load ${skill.name} skill instructions`,
    skill.description.length > 120 ? `${skill.description.slice(0, 117)}...` : skill.description,
  ];
  if (skill.tags && skill.tags.length > 0) {
    queries.push(`${skill.category} skill for ${skill.tags.slice(0, 3).join(', ')}`);
  }
  return queries;
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
  const skillBodies = new Map();

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

      const skillEntry = {
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
      };
      skills.push(skillEntry);
      skillBodies.set(`${catDef.id}/${folder}`, {
        folder,
        rawText,
        markdownBody: extractMarkdownBody(rawText),
        detailUrl: `${BASE_URL}/${catDef.id}/${folder}/`,
        installCommand: `npx skills add danicat/skills --skill ${fm.name} -y`,
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

  // Build llms.txt & root /index.md
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
  llmsTxt += `- [ARD Capability Manifest](${BASE_URL}/.well-known/ai-catalog.json): Agentic Resource Discovery (ARD) manifest with semantic representative queries.\n`;
  llmsTxt += `- [API Catalog](${BASE_URL}/.well-known/api-catalog): RFC 9727 linkset catalog of machine-readable endpoints.\n`;
  for (const cat of categories) {
    const catSkills = skills.filter((s) => s.category === cat.id);
    if (catSkills.length === 0) continue;
    llmsTxt += `- [${cat.name} Index](${BASE_URL}/${cat.id}/llms.txt): Directory-scoped \`llms.txt\` index for ${cat.name} skills.\n`;
  }

  // Build llms-full.txt
  let llmsFullTxt = `# danicat/skills (Full Instructions Catalog)\n\n> Complete collection of all Agent Skills.\n\n---\n`;
  for (const cat of categories) {
    const catSkills = skills
      .filter((s) => s.category === cat.id)
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name));
    for (const s of catSkills) {
      const folderSlug = s.url.split('/').slice(-2, -1)[0];
      const meta = skillBodies.get(`${cat.id}/${folderSlug}`);
      llmsFullTxt += `\n# Skill: ${s.name} (${s.category})\n\n`;
      llmsFullTxt += `> ${s.description}\n\n`;
      llmsFullTxt += `**Web Page**: ${meta.detailUrl}\n`;
      llmsFullTxt += `**Source**: ${s.url}\n`;
      llmsFullTxt += `**Version**: ${s.version}\n`;
      llmsFullTxt += `**Digest**: ${s.digest}\n`;
      llmsFullTxt += `**Install**: \`${meta.installCommand}\`\n\n`;
      llmsFullTxt += `## Instructions\n\n${meta.markdownBody}\n\n---\n`;
    }
  }

  // Build ARD Capability Manifest (/.well-known/ai-catalog.json)
  const ardManifest = {
    specVersion: '1.0',
    host: {
      displayName: 'Danicat Agent Skills Catalog',
      identifier: 'did:web:skills.danicat.dev',
    },
    entries: [
      {
        identifier: 'urn:air:skills.danicat.dev:catalog:agent-skills',
        displayName: 'Danicat Agent Skills Discovery Index',
        type: 'application/json',
        url: `${BASE_URL}/.well-known/agent-skills/index.json`,
        representativeQueries: [
          'discover all available AI agent skills in danicat/skills',
          'list agent skill manifests and sha256 digests',
          'find coding, game-dev, media, workflow, and writing skills',
        ],
      },
      ...skills.map((s) => ({
        identifier: `urn:air:skills.danicat.dev:skill:${s.name.toLowerCase()}`,
        displayName: `${s.name} (${s.category})`,
        type: 'text/markdown',
        url: s.url,
        representativeQueries: buildRepresentativeQueries(s),
      })),
    ],
  };
  const ardJson = JSON.stringify(ardManifest, null, 2) + '\n';

  // Build RFC 9727 API Catalog (/.well-known/api-catalog)
  const apiCatalogManifest = {
    linkset: [
      {
        anchor: `${BASE_URL}/catalog.json`,
        'service-desc': [
          {
            href: SCHEMA_URI,
            type: 'application/schema+json',
          },
        ],
        'service-doc': [
          {
            href: `${BASE_URL}/llms.txt`,
            type: 'text/plain',
          },
        ],
      },
      {
        anchor: `${BASE_URL}/.well-known/agent-skills/index.json`,
        'service-desc': [
          {
            href: SCHEMA_URI,
            type: 'application/schema+json',
          },
        ],
        'service-doc': [
          {
            href: `${BASE_URL}/llms.txt`,
            type: 'text/plain',
          },
        ],
      },
      {
        anchor: `${BASE_URL}/.well-known/ai-catalog.json`,
        'service-doc': [
          {
            href: `${BASE_URL}/llms.txt`,
            type: 'text/plain',
          },
        ],
      },
    ],
  };
  const apiCatalogJson = JSON.stringify(apiCatalogManifest, null, 2) + '\n';

  // Write root artifacts
  const rootCatalogPath = path.join(ROOT_DIR, 'catalog.json');
  const rootLlmsPath = path.join(ROOT_DIR, 'llms.txt');
  fs.writeFileSync(rootCatalogPath, catalogJson, 'utf8');
  fs.writeFileSync(rootLlmsPath, llmsTxt, 'utf8');

  // Sync to static/ and static/.well-known/
  const staticCatalogPath = path.join(ROOT_DIR, 'static', 'catalog.json');
  const staticLlmsPath = path.join(ROOT_DIR, 'static', 'llms.txt');
  const staticLlmsFullPath = path.join(ROOT_DIR, 'static', 'llms-full.txt');
  const staticRootIndexMdPath = path.join(ROOT_DIR, 'static', 'index.md');
  const wellKnownIndexPath = path.join(ROOT_DIR, 'static', '.well-known', 'agent-skills', 'index.json');
  const wellKnownArdPath = path.join(ROOT_DIR, 'static', '.well-known', 'ai-catalog.json');
  const wellKnownApiCatalogPath = path.join(ROOT_DIR, 'static', '.well-known', 'api-catalog');
  const wellKnownApiCatalogJsonPath = path.join(ROOT_DIR, 'static', '.well-known', 'api-catalog.json');

  fs.mkdirSync(path.dirname(staticCatalogPath), { recursive: true });
  fs.mkdirSync(path.dirname(wellKnownIndexPath), { recursive: true });

  fs.writeFileSync(staticCatalogPath, catalogJson, 'utf8');
  fs.writeFileSync(staticLlmsPath, llmsTxt, 'utf8');
  fs.writeFileSync(staticLlmsFullPath, llmsFullTxt, 'utf8');
  fs.writeFileSync(staticRootIndexMdPath, llmsTxt, 'utf8');
  fs.writeFileSync(wellKnownIndexPath, catalogJson, 'utf8');
  fs.writeFileSync(wellKnownArdPath, ardJson, 'utf8');
  fs.writeFileSync(wellKnownApiCatalogPath, apiCatalogJson, 'utf8');
  fs.writeFileSync(wellKnownApiCatalogJsonPath, apiCatalogJson, 'utf8');

  // Write per-category llms.txt & index.md, and per-skill index.md fallbacks
  for (const cat of categories) {
    const catSkills = skills.filter((s) => s.category === cat.id);
    if (catSkills.length === 0) continue;

    let catLlmsTxt = `# ${cat.name} — danicat/skills\n\n> ${cat.description}\n\n## Skills\n\n`;
    for (const s of catSkills) {
      catLlmsTxt += `- [${s.name}](${s.url}): ${s.description}\n`;
    }
    catLlmsTxt += `\n## Optional\n\n`;
    catLlmsTxt += `- [Root Catalog Index](${BASE_URL}/llms.txt): Main \`llms.txt\` directory across all categories.\n`;
    catLlmsTxt += `- [Full Instructions Catalog](${BASE_URL}/llms-full.txt): Complete bundle of all skill instructions.\n`;

    const staticCatDir = path.join(ROOT_DIR, 'static', cat.id);
    fs.mkdirSync(staticCatDir, { recursive: true });
    fs.writeFileSync(path.join(staticCatDir, 'llms.txt'), catLlmsTxt, 'utf8');
    fs.writeFileSync(path.join(staticCatDir, 'index.md'), catLlmsTxt, 'utf8');

    for (const s of catSkills) {
      const folderSlug = s.url.split('/').slice(-2, -1)[0];
      const meta = skillBodies.get(`${cat.id}/${folderSlug}`);
      const staticSkillDir = path.join(staticCatDir, folderSlug);
      fs.mkdirSync(staticSkillDir, { recursive: true });
      fs.writeFileSync(path.join(staticSkillDir, 'index.md'), meta.rawText, 'utf8');
    }
  }

  console.log(
    `✅ Generated catalog (${skills.length} active skills across ${categories.length} categories) -> catalog.json, llms.txt, llms-full.txt, .well-known/{agent-skills/index.json,ai-catalog.json,api-catalog}, and /index.md fallbacks`
  );

  return catalogManifest;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  generateCatalog();
}
