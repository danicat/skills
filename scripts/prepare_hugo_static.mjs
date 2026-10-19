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

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');

export function prepareHugoStatic() {
  const catalogSrc = path.join(ROOT_DIR, 'catalog.json');
  const llmsSrc = path.join(ROOT_DIR, 'llms.txt');

  if (!fs.existsSync(catalogSrc)) {
    throw new Error(`[Fail-Fast] Missing root catalog.json at ${catalogSrc}`);
  }
  if (!fs.existsSync(llmsSrc)) {
    throw new Error(`[Fail-Fast] Missing root llms.txt at ${llmsSrc}`);
  }

  const parsed = JSON.parse(fs.readFileSync(catalogSrc, 'utf8'));
  if (parsed.$schema !== 'https://schemas.agentskills.io/discovery/0.2.0/schema.json') {
    throw new Error(
      `[Fail-Fast] catalog.json is missing required $schema ("https://schemas.agentskills.io/discovery/0.2.0/schema.json")`
    );
  }
  if (!Array.isArray(parsed.skills) || parsed.skills.length === 0) {
    throw new Error('[Fail-Fast] catalog.json has an empty or invalid skills array');
  }
  for (const s of parsed.skills) {
    if (s.type !== 'skill-md' || !s.name || !s.description || !s.url || !s.digest?.startsWith('sha256:')) {
      throw new Error(`[Fail-Fast] Skill entry "${s.name || 'unknown'}" fails Agent Skills Discovery v0.2.0 schema check`);
    }
  }

  const staticCatalogDest = path.join(ROOT_DIR, 'static', 'catalog.json');
  const staticLlmsDest = path.join(ROOT_DIR, 'static', 'llms.txt');
  const wellKnownIndexDest = path.join(ROOT_DIR, 'static', '.well-known', 'agent-skills', 'index.json');

  fs.mkdirSync(path.dirname(staticCatalogDest), { recursive: true });
  fs.mkdirSync(path.dirname(wellKnownIndexDest), { recursive: true });

  fs.copyFileSync(catalogSrc, staticCatalogDest);
  fs.copyFileSync(catalogSrc, wellKnownIndexDest);
  fs.copyFileSync(llmsSrc, staticLlmsDest);

  console.log(
    `✅ Synced catalog.json (${parsed.skills.length} skills) -> static/catalog.json & static/.well-known/agent-skills/index.json, and llms.txt -> static/llms.txt`
  );
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  prepareHugoStatic();
}
