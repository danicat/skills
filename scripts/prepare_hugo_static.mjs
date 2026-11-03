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

const ALLOWED_TOP_LEVEL_KEYS = new Set(['$schema', 'skills']);
const ALLOWED_SKILL_KEYS = new Set(['name', 'type', 'description', 'url', 'digest']);
const ALLOWED_SKILL_TYPES = new Set(['skill-md', 'archive']);

export function prepareHugoStatic() {
  const wellKnownDir = path.join(ROOT_DIR, 'static', '.well-known', 'agent-skills');
  const wellKnownIndex = path.join(wellKnownDir, 'index.json');
  const llmsSrc = path.join(ROOT_DIR, 'llms.txt');

  if (!fs.existsSync(wellKnownIndex)) {
    throw new Error(`[Fail-Fast] Missing discovery index at ${wellKnownIndex}`);
  }
  if (!fs.existsSync(llmsSrc)) {
    throw new Error(`[Fail-Fast] Missing root llms.txt at ${llmsSrc}`);
  }

  const parsed = JSON.parse(fs.readFileSync(wellKnownIndex, 'utf8'));
  const topKeys = Object.keys(parsed);
  for (const key of topKeys) {
    if (!ALLOWED_TOP_LEVEL_KEYS.has(key)) {
      throw new Error(
        `[Fail-Fast] index.json contains non-RFC top-level property "${key}". Only "$schema" and "skills" are allowed.`
      );
    }
  }
  if (parsed.$schema !== 'https://schemas.agentskills.io/discovery/0.2.0/schema.json') {
    throw new Error(
      `[Fail-Fast] index.json is missing required $schema ("https://schemas.agentskills.io/discovery/0.2.0/schema.json")`
    );
  }
  if (!Array.isArray(parsed.skills) || parsed.skills.length === 0) {
    throw new Error('[Fail-Fast] index.json has an empty or invalid skills array');
  }

  for (const s of parsed.skills) {
    for (const k of Object.keys(s)) {
      if (!ALLOWED_SKILL_KEYS.has(k)) {
        throw new Error(
          `[Fail-Fast] Skill entry "${s.name || 'unknown'}" contains non-RFC property "${k}"`
        );
      }
    }
    if (
      !ALLOWED_SKILL_TYPES.has(s.type) ||
      !s.name ||
      !s.description ||
      !s.url ||
      !/^sha256:[0-9a-f]{64}$/.test(s.digest || '')
    ) {
      throw new Error(`[Fail-Fast] Skill entry "${s.name || 'unknown'}" fails Agent Skills Discovery v0.2.0 schema check`);
    }

    if (s.type === 'archive') {
      const archivePath = path.join(wellKnownDir, s.url);
      if (!fs.existsSync(archivePath)) {
        throw new Error(`[Fail-Fast] Missing archive artifact for skill "${s.name}": ${archivePath}`);
      }
      const actualDigest = 'sha256:' + crypto.createHash('sha256').update(fs.readFileSync(archivePath)).digest('hex');
      if (actualDigest !== s.digest) {
        throw new Error(
          `[Fail-Fast] Archive digest mismatch for "${s.name}": expected ${s.digest}, got ${actualDigest}`
        );
      }
    }
  }

  const staticLlmsDest = path.join(ROOT_DIR, 'static', 'llms.txt');
  const staticIndexMdDest = path.join(ROOT_DIR, 'static', 'index.md');
  const staticLlmsFullDest = path.join(ROOT_DIR, 'static', 'llms-full.txt');
  const wellKnownArdDest = path.join(ROOT_DIR, 'static', '.well-known', 'ai-catalog.json');
  const wellKnownApiCatalogDest = path.join(ROOT_DIR, 'static', '.well-known', 'api-catalog');

  fs.mkdirSync(path.dirname(staticLlmsDest), { recursive: true });
  fs.copyFileSync(llmsSrc, staticLlmsDest);
  fs.copyFileSync(llmsSrc, staticIndexMdDest);

  for (const reqStatic of [staticLlmsFullDest, wellKnownArdDest, wellKnownApiCatalogDest]) {
    if (!fs.existsSync(reqStatic)) {
      throw new Error(
        `[Fail-Fast] Missing generated static discovery file: ${path.relative(ROOT_DIR, reqStatic)}. Run: node scripts/generate_catalog.mjs`
      );
    }
  }

  console.log(
    `✅ Verified static/.well-known/agent-skills/index.json (${parsed.skills.length} skills) & synced llms.txt -> static/llms.txt & static/index.md`
  );
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  prepareHugoStatic();
}
