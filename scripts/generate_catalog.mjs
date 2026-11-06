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
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');

const SCHEMA_URI = 'https://schemas.agentskills.io/discovery/0.2.0/schema.json';
const BASE_URL = 'https://skills.danicat.dev';

const CATEGORY_ORDER = [
  { id: 'workflows', emoji: '🔄' },
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

/**
 * Recursively collects all files in a skill directory relative to skillDir,
 * sorted lexicographically for deterministic archive creation.
 */
function collectSkillFiles(skillDir, relPrefix = '') {
  const entries = fs.readdirSync(skillDir, { withFileTypes: true }).sort((a, b) =>
    a.name.localeCompare(b.name)
  );
  const files = [];
  for (const entry of entries) {
    if (entry.name === '.DS_Store' || entry.name.startsWith('.')) continue;
    const relPath = relPrefix ? `${relPrefix}/${entry.name}` : entry.name;
    const fullPath = path.join(skillDir, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectSkillFiles(fullPath, relPath));
    } else if (entry.isFile()) {
      files.push({ relPath, fullPath });
    }
  }
  return files;
}

/**
 * Creates a deterministic POSIX USTAR tar header (512 bytes) with mtime=0, uid=0, gid=0.
 */
function createUstarHeader(relPath, size, mode) {
  const header = Buffer.alloc(512, 0);

  let name = relPath;
  let prefix = '';
  if (Buffer.byteLength(name, 'utf8') > 100) {
    const slashIdx = name.lastIndexOf('/');
    if (slashIdx === -1) {
      throw new Error(`[Fail-Fast] Tar entry filename exceeds 100 bytes: ${relPath}`);
    }
    prefix = name.slice(0, slashIdx);
    name = name.slice(slashIdx + 1);
    if (Buffer.byteLength(name, 'utf8') > 100 || Buffer.byteLength(prefix, 'utf8') > 155) {
      throw new Error(`[Fail-Fast] Tar entry path exceeds USTAR limits: ${relPath}`);
    }
  }

  const writeOctal = (val, offset, length) => {
    const str = val.toString(8).padStart(length - 1, '0') + '\0';
    header.write(str, offset, length, 'ascii');
  };

  header.write(name, 0, 100, 'utf8');
  writeOctal(mode, 100, 8);
  writeOctal(0, 108, 8); // uid = 0
  writeOctal(0, 116, 8); // gid = 0
  writeOctal(size, 124, 12);
  writeOctal(0, 136, 12); // mtime = 0 (1970-01-01T00:00:00Z)
  header.fill(0x20, 148, 156); // checksum placeholder (8 spaces)
  header.write('0', 156, 1, 'ascii'); // typeflag = '0' (regular file)
  header.write('ustar\0', 257, 6, 'ascii');
  header.write('00', 263, 2, 'ascii');
  header.write('root', 265, 32, 'ascii');
  header.write('root', 297, 32, 'ascii');
  if (prefix) {
    header.write(prefix, 345, 155, 'utf8');
  }

  let chksum = 0;
  for (let i = 0; i < 512; i++) {
    chksum += header[i];
  }
  const chkStr = chksum.toString(8).padStart(6, '0') + '\0 ';
  header.write(chkStr, 148, 8, 'ascii');

  return header;
}

/**
 * Builds a deterministic .tar.gz buffer (gzip OS byte = 3 Unix, mtime = 0).
 */
function buildDeterministicTarGz(files) {
  const blocks = [];
  for (const file of files) {
    const content = fs.readFileSync(file.fullPath);
    const isExecutable = file.relPath.startsWith('scripts/') && /\.(sh|py|mjs|js)$/.test(file.relPath);
    const mode = isExecutable ? 0o755 : 0o644;
    const header = createUstarHeader(file.relPath, content.length, mode);
    blocks.push(header);
    blocks.push(content);
    const remainder = content.length % 512;
    if (remainder !== 0) {
      blocks.push(Buffer.alloc(512 - remainder, 0));
    }
  }
  // End-of-archive marker: two 512-byte zero blocks
  blocks.push(Buffer.alloc(1024, 0));

  const tarBuffer = Buffer.concat(blocks);
  const gzBuffer = zlib.gzipSync(tarBuffer, { level: 9 });
  // Zero out gzip header mtime (bytes 4..7) and normalize OS byte (byte 9 = 3 for Unix)
  gzBuffer[4] = 0;
  gzBuffer[5] = 0;
  gzBuffer[6] = 0;
  gzBuffer[7] = 0;
  gzBuffer[9] = 3;
  return gzBuffer;
}

export function generateCatalog() {
  const translations = readRequiredJson('data/translations.json');
  const freshnessMap = readRequiredJson('data/freshness.json');
  const pluginsConfig = readRequiredJson('data/plugins.json');

  const enCategories = translations?.en?.categories;
  if (!enCategories) {
    throw new Error('[Fail-Fast] Missing en.categories in data/translations.json');
  }

  const wellKnownDir = path.join(ROOT_DIR, 'static', '.well-known', 'agent-skills');
  fs.mkdirSync(wellKnownDir, { recursive: true });

  // Clean up any stale .tar.gz archives in static/.well-known/agent-skills/
  for (const existing of fs.readdirSync(wellKnownDir)) {
    if (existing.endsWith('.tar.gz')) {
      fs.unlinkSync(path.join(wellKnownDir, existing));
    }
  }

  const categories = [];
  const discoverySkills = [];
  const richSkills = [];
  const richPlugins = [];
  const skillBodies = new Map();
  let archiveCount = 0;
  let skillMdCount = 0;

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
      const skillDir = path.join(catDir, folder);
      const relSkillPath = `${catDef.id}/${folder}/SKILL.md`;
      const fullSkillPath = path.join(ROOT_DIR, relSkillPath);
      if (!fs.existsSync(fullSkillPath)) {
        continue;
      }

      const rawBytes = fs.readFileSync(fullSkillPath);
      const rawText = rawBytes.toString('utf8');
      const fm = parseFrontmatterStrict(rawText, relSkillPath);

      const tags = fm.metadata.tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);

      const skillId = fm.name.toLowerCase();
      if (!freshnessMap[skillId]) {
        throw new Error(
          `[Fail-Fast] Skill "${skillId}" is missing from data/freshness.json. Run: node scripts/update_freshness.mjs`
        );
      }

      const files = collectSkillFiles(skillDir);
      const isMultiFile = files.some((f) => f.relPath !== 'SKILL.md');
      const skillMdUrl = `${BASE_URL}/${catDef.id}/${folder}/SKILL.md`;

      let entryType;
      let entryUrl;
      let digestHex;

      if (isMultiFile) {
        entryType = 'archive';
        const archiveFileName = `${folder}.tar.gz`;
        entryUrl = `${BASE_URL}/.well-known/agent-skills/${archiveFileName}`;
        const archiveBuffer = buildDeterministicTarGz(files);
        digestHex = crypto.createHash('sha256').update(archiveBuffer).digest('hex');
        fs.writeFileSync(path.join(wellKnownDir, archiveFileName), archiveBuffer);
        archiveCount++;
      } else {
        entryType = 'skill-md';
        entryUrl = skillMdUrl;
        digestHex = crypto.createHash('sha256').update(rawBytes).digest('hex');
        skillMdCount++;
      }

      // Strict Cloudflare Agent Skills Discovery RFC v0.2.0 entry (5 fields only)
      discoverySkills.push({
        name: fm.name,
        type: entryType,
        description: fm.description.trim(),
        url: entryUrl,
        digest: `sha256:${digestHex}`,
      });

      richSkills.push({
        name: fm.name,
        folder,
        type: entryType,
        description: fm.description.trim(),
        category: fm.metadata.category,
        tags,
        author: fm.metadata.author,
        version: fm.metadata.version,
        license: fm.license,
        url: skillMdUrl,
        discoveryUrl: entryUrl,
        digest: `sha256:${digestHex}`,
      });

      skillBodies.set(skillId, {
        folder,
        staticRelDir: `${catDef.id}/${folder}`,
        rawText,
        markdownBody: extractMarkdownBody(rawText),
        detailUrl: `${BASE_URL}/${catDef.id}/${folder}/`,
        installCommand: `npx skills add danicat/skills --skill ${fm.name} -y`,
      });
    }
  }

  // Scan plugins/<pluginId>/ and their bundled skills
  for (const [pluginId, pCfg] of Object.entries(pluginsConfig).sort(([a], [b]) => a.localeCompare(b))) {
    const pluginDir = path.join(ROOT_DIR, 'plugins', pluginId);
    const manifestPath = path.join(pluginDir, 'plugin.json');
    const readmePath = path.join(pluginDir, 'README.md');
    if (!fs.existsSync(manifestPath) || !fs.existsSync(readmePath)) {
      throw new Error(
        `[Fail-Fast] Missing vendored plugin files for "${pluginId}". Run: node scripts/sync_plugins.mjs`
      );
    }

    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    const readmeText = fs.readFileSync(readmePath, 'utf8');
    const skillsRoot = path.join(pluginDir, manifest.skills || 'skills');
    const skillFolders = fs.existsSync(skillsRoot)
      ? fs
          .readdirSync(skillsRoot, { withFileTypes: true })
          .filter((d) => d.isDirectory())
          .map((d) => d.name)
          .sort()
      : [];

    const bundledSkillNames = [];

    for (const folder of skillFolders) {
      const skillDir = path.join(skillsRoot, folder);
      const relSkillPath = `plugins/${pluginId}/skills/${folder}/SKILL.md`;
      const fullSkillPath = path.join(ROOT_DIR, relSkillPath);
      if (!fs.existsSync(fullSkillPath)) {
        continue;
      }

      const rawBytes = fs.readFileSync(fullSkillPath);
      const rawText = rawBytes.toString('utf8');
      const fm = parseFrontmatterStrict(rawText, relSkillPath);

      const tags = fm.metadata.tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);

      const skillId = fm.name.toLowerCase();
      bundledSkillNames.push(fm.name);

      const files = collectSkillFiles(skillDir);
      const isMultiFile = files.some((f) => f.relPath !== 'SKILL.md');
      const skillMdUrl = `${BASE_URL}/plugins/${pluginId}/skills/${folder}/SKILL.md`;

      let entryType;
      let entryUrl;
      let digestHex;

      if (isMultiFile) {
        entryType = 'archive';
        const archiveFileName = `${folder}.tar.gz`;
        entryUrl = `${BASE_URL}/.well-known/agent-skills/${archiveFileName}`;
        const archiveBuffer = buildDeterministicTarGz(files);
        digestHex = crypto.createHash('sha256').update(archiveBuffer).digest('hex');
        fs.writeFileSync(path.join(wellKnownDir, archiveFileName), archiveBuffer);
        archiveCount++;
      } else {
        entryType = 'skill-md';
        entryUrl = skillMdUrl;
        digestHex = crypto.createHash('sha256').update(rawBytes).digest('hex');
        skillMdCount++;
      }

      discoverySkills.push({
        name: fm.name,
        type: entryType,
        description: fm.description.trim(),
        url: entryUrl,
        digest: `sha256:${digestHex}`,
      });

      richSkills.push({
        name: fm.name,
        folder,
        pluginId,
        pluginDisplayName: manifest.displayName || pCfg.displayName || pluginId,
        type: entryType,
        description: fm.description.trim(),
        category: fm.metadata.category,
        tags,
        author: fm.metadata.author,
        version: fm.metadata.version,
        license: fm.license,
        url: skillMdUrl,
        discoveryUrl: entryUrl,
        digest: `sha256:${digestHex}`,
      });

      skillBodies.set(skillId, {
        folder,
        staticRelDir: `plugins/${pluginId}/skills/${folder}`,
        rawText,
        markdownBody: extractMarkdownBody(rawText),
        detailUrl: `${BASE_URL}/plugins/${pluginId}/skills/${folder}/`,
        installCommand: pCfg.installCommand,
      });
    }

    richPlugins.push({
      id: pluginId,
      displayName: manifest.displayName || pCfg.displayName || pluginId,
      description: manifest.description,
      version: manifest.version,
      tag: pCfg.tag,
      repo: pCfg.repo,
      category: pCfg.category || manifest.category || 'writing',
      url: `${BASE_URL}/plugins/${pluginId}/README.md`,
      detailUrl: `${BASE_URL}/plugins/${pluginId}/`,
      installCommand: pCfg.installCommand || `npx skills add ${pCfg.repo} -y`,
      readmeText,
      skillNames: bundledSkillNames,
    });
  }

  // Strict Cloudflare Agent Skills Discovery RFC v0.2.0 top-level object ($schema + skills only)
  const discoveryManifest = {
    $schema: SCHEMA_URI,
    skills: discoverySkills,
  };

  const indexJson = JSON.stringify(discoveryManifest, null, 2) + '\n';

  // Build llms.txt & root /index.md
  let llmsTxt = `# danicat/skills\n\n> A curated collection of specialized Agent Skills and Antigravity Plugins for coding, game development, generative media, writing, and standards.\n\n`;
  if (richPlugins.length > 0) {
    llmsTxt += `## Plugins\n\n`;
    for (const p of richPlugins) {
      llmsTxt += `- [${p.displayName}](${p.url}): ${p.description} (v${p.version} — includes skills: ${p.skillNames.join(', ')})\n`;
    }
    llmsTxt += `\n`;
  }
  for (const cat of categories) {
    const catSkills = richSkills.filter((s) => s.category === cat.id);
    if (catSkills.length === 0) continue;
    llmsTxt += `## ${cat.name}\n\n`;
    for (const s of catSkills) {
      llmsTxt += `- [${s.name}](${s.url}): ${s.description}\n`;
    }
    llmsTxt += `\n`;
  }
  llmsTxt += `## Optional\n\n`;
  llmsTxt += `- [Full Instructions Catalog](${BASE_URL}/llms-full.txt): Complete bundle of all ${richSkills.length} skill instructions in a single file for large-context models.\n`;
  llmsTxt += `- [Agent Skills Discovery Index](${BASE_URL}/.well-known/agent-skills/index.json): RFC v0.2.0 well-known discovery index with SHA-256 digests.\n`;
  llmsTxt += `- [ARD Capability Manifest](${BASE_URL}/.well-known/ai-catalog.json): Agentic Resource Discovery (ARD) manifest with semantic representative queries.\n`;
  llmsTxt += `- [API Catalog](${BASE_URL}/.well-known/api-catalog): RFC 9727 linkset catalog of machine-readable endpoints.\n`;
  if (richPlugins.length > 0) {
    llmsTxt += `- [Plugins Index](${BASE_URL}/plugins/llms.txt): Directory-scoped \`llms.txt\` index for Antigravity plugins.\n`;
  }
  for (const cat of categories) {
    const catSkills = richSkills.filter((s) => s.category === cat.id);
    if (catSkills.length === 0) continue;
    llmsTxt += `- [${cat.name} Index](${BASE_URL}/${cat.id}/llms.txt): Directory-scoped \`llms.txt\` index for ${cat.name} skills.\n`;
  }

  // Build llms-full.txt
  let llmsFullTxt = `# danicat/skills (Full Instructions Catalog)\n\n> Complete collection of all Agent Skills and Antigravity Plugins.\n\n---\n`;
  for (const p of richPlugins) {
    llmsFullTxt += `\n# Plugin: ${p.displayName} (v${p.version})\n\n`;
    llmsFullTxt += `> ${p.description}\n\n`;
    llmsFullTxt += `**Web Page**: ${p.detailUrl}\n`;
    llmsFullTxt += `**Source**: ${p.url}\n`;
    llmsFullTxt += `**Install**: \`${p.installCommand}\`\n\n`;
    llmsFullTxt += `${p.readmeText.trim()}\n\n---\n`;
  }
  for (const cat of categories) {
    const catSkills = richSkills
      .filter((s) => s.category === cat.id)
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name));
    for (const s of catSkills) {
      const meta = skillBodies.get(s.name.toLowerCase());
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
      ...richPlugins.map((p) => ({
        identifier: `urn:air:skills.danicat.dev:plugin:${p.id}`,
        displayName: `${p.displayName} (plugin)`,
        type: 'text/markdown',
        url: p.url,
        representativeQueries: [
          `install ${p.id} plugin for Antigravity`,
          p.description,
          `writing plugin with ${p.skillNames.join(', ')} skills`,
        ],
      })),
      ...richSkills.map((s) => ({
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

  // Write root llms.txt
  const rootLlmsPath = path.join(ROOT_DIR, 'llms.txt');
  fs.writeFileSync(rootLlmsPath, llmsTxt, 'utf8');

  // Sync to static/ and static/.well-known/
  const staticLlmsPath = path.join(ROOT_DIR, 'static', 'llms.txt');
  const staticLlmsFullPath = path.join(ROOT_DIR, 'static', 'llms-full.txt');
  const staticRootIndexMdPath = path.join(ROOT_DIR, 'static', 'index.md');
  const wellKnownIndexPath = path.join(wellKnownDir, 'index.json');
  const wellKnownArdPath = path.join(ROOT_DIR, 'static', '.well-known', 'ai-catalog.json');
  const wellKnownApiCatalogPath = path.join(ROOT_DIR, 'static', '.well-known', 'api-catalog');
  const wellKnownApiCatalogJsonPath = path.join(ROOT_DIR, 'static', '.well-known', 'api-catalog.json');

  fs.mkdirSync(path.dirname(staticLlmsPath), { recursive: true });

  fs.writeFileSync(staticLlmsPath, llmsTxt, 'utf8');
  fs.writeFileSync(staticLlmsFullPath, llmsFullTxt, 'utf8');
  fs.writeFileSync(staticRootIndexMdPath, llmsTxt, 'utf8');
  fs.writeFileSync(wellKnownIndexPath, indexJson, 'utf8');
  fs.writeFileSync(wellKnownArdPath, ardJson, 'utf8');
  fs.writeFileSync(wellKnownApiCatalogPath, apiCatalogJson, 'utf8');
  fs.writeFileSync(wellKnownApiCatalogJsonPath, apiCatalogJson, 'utf8');

  // Write per-category llms.txt & index.md, and per-skill index.md fallbacks
  for (const cat of categories) {
    const catSkills = richSkills.filter((s) => s.category === cat.id);
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
      const meta = skillBodies.get(s.name.toLowerCase());
      const staticSkillDir = path.join(ROOT_DIR, 'static', meta.staticRelDir);
      fs.mkdirSync(staticSkillDir, { recursive: true });
      fs.writeFileSync(path.join(staticSkillDir, 'index.md'), meta.rawText, 'utf8');
    }
  }

  // Write static/plugins/llms.txt, static/plugins/index.md, and per-plugin index.md fallbacks
  if (richPlugins.length > 0) {
    const pluginsTrans = enCategories.plugins || {
      name: 'Plugins',
      description: 'Full-featured Antigravity plugins bundling sidecar editors, MCP servers, rules, and multi-stage skills.',
    };
    let pluginsLlmsTxt = `# ${pluginsTrans.name} — danicat/skills\n\n> ${pluginsTrans.description}\n\n## Plugins\n\n`;
    for (const p of richPlugins) {
      pluginsLlmsTxt += `- [${p.displayName}](${p.url}): ${p.description} (v${p.version})\n`;
      const pSkills = richSkills.filter((s) => s.pluginId === p.id);
      for (const s of pSkills) {
        pluginsLlmsTxt += `  - [${s.name}](${s.url}): ${s.description}\n`;
      }
    }
    pluginsLlmsTxt += `\n## Optional\n\n`;
    pluginsLlmsTxt += `- [Root Catalog Index](${BASE_URL}/llms.txt): Main \`llms.txt\` directory across all categories.\n`;
    pluginsLlmsTxt += `- [Full Instructions Catalog](${BASE_URL}/llms-full.txt): Complete bundle of all skill instructions.\n`;

    const staticPluginsDir = path.join(ROOT_DIR, 'static', 'plugins');
    fs.mkdirSync(staticPluginsDir, { recursive: true });
    fs.writeFileSync(path.join(staticPluginsDir, 'llms.txt'), pluginsLlmsTxt, 'utf8');
    fs.writeFileSync(path.join(staticPluginsDir, 'index.md'), pluginsLlmsTxt, 'utf8');

    for (const p of richPlugins) {
      const staticPluginDir = path.join(staticPluginsDir, p.id);
      fs.mkdirSync(staticPluginDir, { recursive: true });
      fs.writeFileSync(path.join(staticPluginDir, 'index.md'), p.readmeText, 'utf8');
    }
  }

  console.log(
    `✅ Generated RFC v0.2.0 discovery index (${discoverySkills.length} skills: ${archiveCount} archives, ${skillMdCount} standalone skill-md, ${richPlugins.length} plugins) -> static/.well-known/agent-skills/index.json, llms.txt, llms-full.txt, .well-known/{ai-catalog.json,api-catalog}, and /index.md fallbacks`
  );

  return discoveryManifest;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  generateCatalog();
}
