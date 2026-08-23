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

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const CATALOG_URL = 'https://skills.danicat.dev';

const VALID_CATEGORIES = [
  'game-dev',
  'media',
  'coding',
  'agents',
  'writing',
  'analytics',
  'standards'
];

function extractFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) {
    return { data: {}, body: content };
  }
  const rawYaml = match[1];
  const body = match[2];

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

        if (val === '>' || val === '|' || val === '>-' || val === '|-') {
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

  return { data, body };
}

function formatDescriptionYaml(desc) {
  if (!desc) return 'description: ""';
  const words = desc.trim().split(/\s+/);
  const lines = [];
  let currentLine = '  ';
  for (const word of words) {
    if ((currentLine + ' ' + word).length > 80) {
      lines.push(currentLine);
      currentLine = '  ' + word;
    } else {
      currentLine = currentLine === '  ' ? '  ' + word : currentLine + ' ' + word;
    }
  }
  if (currentLine.trim()) {
    lines.push(currentLine);
  }
  return `description: >\n${lines.join('\n')}`;
}

let updatedCount = 0;

for (const cat of VALID_CATEGORIES) {
  const catDir = path.join(ROOT_DIR, cat);
  if (!fs.existsSync(catDir)) continue;

  const skillDirs = fs.readdirSync(catDir, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);

  for (const skillName of skillDirs) {
    const skillPath = path.join(catDir, skillName, 'SKILL.md');
    if (!fs.existsSync(skillPath)) continue;

    const raw = fs.readFileSync(skillPath, 'utf8');
    const { data, body } = extractFrontmatter(raw);

    const name = data.name || skillName;
    const desc = data.description || '';
    const license = data.license || 'Apache-2.0';
    const compatibility = data['compatibility'] || null;
    const allowedTools = data['allowed-tools'] || null;

    const meta = data.metadata || {};
    const category = meta.category || cat;
    const tags = meta.tags || skillName;
    const author = meta.author || 'Daniela Petruzalek (daniela@danicat.dev)';
    const version = meta.version || '0.1.0';

    const formattedDesc = formatDescriptionYaml(desc);

    let frontmatter = `---\nname: ${name}\n${formattedDesc}\nlicense: ${license}\n`;
    if (compatibility) frontmatter += `compatibility: ${compatibility}\n`;
    if (allowedTools) frontmatter += `allowed-tools: ${allowedTools}\n`;

    frontmatter += `metadata:\n`;
    frontmatter += `  category: ${category}\n`;
    frontmatter += `  tags: "${tags}"\n`;
    frontmatter += `  author: ${author}\n`;
    frontmatter += `  version: "${version}"\n`;
    frontmatter += `  catalog: ${CATALOG_URL}\n`;
    frontmatter += `---\n\n`;

    const newContent = frontmatter + body.trim() + '\n';
    fs.writeFileSync(skillPath, newContent);
    updatedCount++;
  }
}

console.log(`Successfully standardized frontmatter with single catalog coordinate across ${updatedCount} skills!`);
