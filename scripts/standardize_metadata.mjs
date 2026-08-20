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
const DOMAIN = 'https://skills.danicat.dev';
const REPO_URL = 'https://github.com/danicat/skills';

const SKILL_CONFIGS = [
  // Agents & Meta-Tooling
  {
    category: 'agents',
    skill: 'a2ui-developer-guide',
    version: '0.1.0',
    tags: 'agents, a2ui, protocol, ui, streaming, json-lines, components'
  },
  {
    category: 'agents',
    skill: 'double-diamond',
    version: '0.1.0',
    tags: 'agents, double-diamond, agile, swarm, orchestration, architecture, planning'
  },
  {
    category: 'agents',
    skill: 'skill-optimizer',
    version: '0.3.2',
    tags: 'agents, skill-optimizer, evals, benchmarks, testing, authoring, specification'
  },
  {
    category: 'agents',
    skill: 'swarm-coding',
    version: '0.1.0',
    tags: 'agents, swarm-coding, multi-agent, coordinator, parallelism, worktrees'
  },

  // Coding & Tooling
  {
    category: 'coding',
    skill: 'engineering-flow',
    version: '0.1.0',
    tags: 'coding, git, hygiene, conventional-commits, changelog, workflow, quality'
  },
  {
    category: 'coding',
    skill: 'find-examples',
    version: '0.1.0',
    tags: 'coding, examples, apis, sdk, references, patterns, integrations'
  },
  {
    category: 'coding',
    skill: 'godoctor',
    version: '0.34.0',
    tags: 'coding, golang, ast, refactoring, testing, mutation, selene, testquery'
  },
  {
    category: 'coding',
    skill: 'latest-version',
    version: '0.1.0',
    tags: 'coding, package-managers, dependencies, npm, pypi, cargo, go-proxy'
  },
  {
    category: 'coding',
    skill: 'pyhd',
    version: '0.1.0',
    tags: 'coding, python, uv, packaging, typing, ruff, formatting, pyproject'
  },

  // Game Development
  {
    category: 'game-dev',
    skill: 'ebitengineer',
    version: '1.2.0',
    tags: 'game-dev, ebitengine, golang, 2d, shaders, wasm, audio, architecture'
  },
  {
    category: 'game-dev',
    skill: 'game-design',
    version: '1.0.0',
    tags: 'game-dev, gdd, mechanics, game-design, narrative, prototyping'
  },
  {
    category: 'game-dev',
    skill: 'procedural-art',
    version: '1.0.0',
    tags: 'game-dev, procedural-art, sprites, pixel-art, vector, shaders, particles'
  },
  {
    category: 'game-dev',
    skill: 'procedural-composer',
    version: '1.0.0',
    tags: 'game-dev, music, chiptune, synth, procedural-audio, sfx, bytebeat'
  },
  {
    category: 'game-dev',
    skill: 'sprite-animation',
    version: '1.0.0',
    tags: 'game-dev, spritesheet, animation, keyframes, timing, ebitengine'
  },
  {
    category: 'game-dev',
    skill: 'vibe-game-developer',
    version: '1.0.0',
    tags: 'game-dev, ebitengine, gemini, game-developer, orchestrator, 2d'
  },

  // Generative Media & Audio
  {
    category: 'media',
    skill: 'lyria',
    version: '0.1.0',
    tags: 'media, lyria, music-generation, stereo, synth, midi, generative-audio'
  },
  {
    category: 'media',
    skill: 'nano-banana',
    version: '0.1.0',
    tags: 'media, nano-banana, image-generation, gemini, art, visual-assets'
  },

  // Engineering Standards
  {
    category: 'standards',
    skill: 'adr-template',
    version: '0.1.0',
    tags: 'standards, adr, architecture, decision-records, documentation, design'
  },
  {
    category: 'standards',
    skill: 'rfc-template',
    version: '0.1.0',
    tags: 'standards, rfc, technical-proposals, consensus, architecture, design-docs'
  },

  // Technical Writing & Content
  {
    category: 'writing',
    skill: 'buffer',
    version: '0.1.0',
    tags: 'writing, social-media, buffer, publishing, automation, cli'
  },
  {
    category: 'writing',
    skill: 'buffer-analytics',
    version: '0.1.0',
    tags: 'writing, analytics, buffer, social-metrics, sqlite, engagement, sql'
  },
  {
    category: 'writing',
    skill: 'deslopify',
    version: '0.1.0',
    tags: 'writing, deslopify, editorial, tropes, ai-cleanup, style, prose'
  },
  {
    category: 'writing',
    skill: 'google-analytics',
    version: '0.1.0',
    tags: 'writing, analytics, ga4, google-analytics, sqlite, metrics, dwell-time'
  },
  {
    category: 'writing',
    skill: 'google-blog-style',
    version: '0.2.0',
    tags: 'writing, style-guide, google-developers-blog, editorial, compliance'
  },
  {
    category: 'writing',
    skill: 'google-codelab-authoring',
    version: '0.1.0',
    tags: 'writing, codelab, claat, tutorials, hands-on, developer-guides'
  },
  {
    category: 'writing',
    skill: 'inverted-pyramid',
    version: '0.1.0',
    tags: 'writing, inverted-pyramid, information-hierarchy, scannable-docs, lead'
  },
  {
    category: 'writing',
    skill: 'search-analytics',
    version: '0.1.0',
    tags: 'writing, search-console, seo-analytics, sqlite, keywords, gsc, rankings'
  },
  {
    category: 'writing',
    skill: 'seo-optimizer',
    version: '0.1.0',
    tags: 'writing, seo, geo, json-ld, llms-txt, keywords, search-engines'
  },
  {
    category: 'writing',
    skill: 'social-copy',
    version: '0.1.0',
    tags: 'writing, social-copy, developer-marketing, linkedin, twitter, bluesky'
  }
];

function extractDescriptionAndBody(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) {
    return { description: '', body: content };
  }
  const rawYaml = match[1];
  const body = match[2];

  // Extract description
  let description = '';
  const descMatch = rawYaml.match(/description:\s*(?:>|>-|\||\|-)?\r?\n([\s\S]*?)(?=\n[a-zA-Z0-9_-]+:|$)/);
  if (descMatch) {
    description = descMatch[1]
      .split(/\r?\n/)
      .map(line => line.trim())
      .filter(Boolean)
      .join(' ');
  } else {
    const inlineDescMatch = rawYaml.match(/description:\s*(.*)/);
    if (inlineDescMatch) {
      description = inlineDescMatch[1].replace(/^["']|["']$/g, '').trim();
    }
  }

  return { description, body };
}

function formatDescriptionYaml(desc) {
  if (!desc) return 'description: ""';
  const words = desc.split(/\s+/);
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

for (const cfg of SKILL_CONFIGS) {
  const skillPath = path.join(ROOT_DIR, cfg.category, cfg.skill, 'SKILL.md');
  if (!fs.existsSync(skillPath)) {
    console.warn(`File not found: ${skillPath}`);
    continue;
  }

  const raw = fs.readFileSync(skillPath, 'utf8');
  const { description, body } = extractDescriptionAndBody(raw);

  const formattedDesc = formatDescriptionYaml(description);

  const frontmatter = `---
name: ${cfg.skill}
${formattedDesc}
license: Apache-2.0
metadata:
  category: ${cfg.category}
  tags: "${cfg.tags}"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "${cfg.version}"
  homepage: ${DOMAIN}/${cfg.category}/${cfg.skill}/
  canonical: ${DOMAIN}/${cfg.category}/${cfg.skill}/SKILL.md
  repository: ${REPO_URL}/tree/main/${cfg.category}/${cfg.skill}
---

${body.trim()}
`;

  fs.writeFileSync(skillPath, frontmatter);
  updatedCount++;
}

console.log(`Successfully standardized frontmatter for ${updatedCount} skills!`);
