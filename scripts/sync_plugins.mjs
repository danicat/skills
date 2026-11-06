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

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const PLUGINS_JSON_PATH = path.join(ROOT_DIR, 'data', 'plugins.json');
const PLUGINS_DIR = path.join(ROOT_DIR, 'plugins');

function shouldVendorPath(relPath) {
  if (
    relPath === 'plugin.json' ||
    relPath === 'mcp_config.json' ||
    relPath === 'README.md' ||
    relPath === 'llms.txt' ||
    relPath === 'LICENSE'
  ) {
    return true;
  }
  if (relPath.startsWith('assets/') || relPath.startsWith('rules/') || relPath.startsWith('skills/')) {
    return true;
  }
  if (/^sidecars\/[^/]+\/sidecar\.json$/.test(relPath)) {
    return true;
  }
  return false;
}

function injectSkillProvenance(rawMd, repoUrl, pluginId) {
  const match = rawMd.match(/^(---\r?\n)([\s\S]*?)(\r?\n---)/);
  if (!match) {
    throw new Error(`[Fail-Fast] Missing YAML frontmatter in skill inside plugin "${pluginId}"`);
  }
  let yaml = match[2];
  const hasRepository = /^\s{2,}repository:/m.test(yaml);
  const hasCatalog = /^\s{2,}catalog:/m.test(yaml);
  const hasPlugin = /^\s{2,}plugin:/m.test(yaml);

  const additions = [];
  if (!hasRepository && !hasCatalog) {
    additions.push(`  repository: ${repoUrl}`);
  }
  if (!hasPlugin) {
    additions.push(`  plugin: ${pluginId}`);
  }
  if (additions.length === 0) {
    return rawMd;
  }

  yaml = yaml.trimEnd() + '\n' + additions.join('\n');
  return `${match[1]}${yaml}${match[3]}${rawMd.slice(match[0].length)}`;
}

function isSubstantiveCommit(repoDir, sha, subject, relPath, isInitial) {
  if (isInitial) return true;
  const diff = execFileSync(
    'git',
    ['show', '-M', '--format=', sha, '--', relPath],
    { cwd: repoDir, encoding: 'utf8' }
  );
  const changedLines = diff
    .split('\n')
    .filter((l) => (l.startsWith('+') && !l.startsWith('+++')) || (l.startsWith('-') && !l.startsWith('---')));

  const substantiveLines = changedLines.filter((l) => {
    const line = l.slice(1).trim();
    if (!line || line === '---') return false;
    if (/^(name|category|tags|author|license|catalog|canonical|version|repository|plugin):/.test(line)) return false;
    if (
      /^(#|\/\/|\*)\s*(Copyright 202\d|SPDX-License|Licensed under|you may not use|http:\/\/www\.apache\.org|Unless required|See the License|limitations under)/i.test(
        line
      )
    ) {
      return false;
    }
    return true;
  });

  return substantiveLines.length >= 4;
}

function extractGitHistoryAtTag(repoDir, tagRef, relPath) {
  const args = ['log'];
  if (relPath) {
    args.push('--follow');
  }
  args.push('--format=%H|%h|%aI|%s', tagRef);
  if (relPath) {
    args.push('--', relPath);
  }
  const logLines = execFileSync('git', args, { cwd: repoDir, encoding: 'utf8' })
    .trim()
    .split('\n')
    .filter(Boolean);

  if (logLines.length === 0) {
    throw new Error(`[Fail-Fast] No git history found at ${tagRef} for ${relPath || 'root'}`);
  }

  let chosenLine = logLines[0];
  if (relPath) {
    chosenLine = logLines[logLines.length - 1];
    for (let i = 0; i < logLines.length; i++) {
      const [fullSha, , , subj] = logLines[i].split('|');
      const isInitial = i === logLines.length - 1;
      if (isSubstantiveCommit(repoDir, fullSha, subj || '', relPath, isInitial)) {
        chosenLine = logLines[i];
        break;
      }
    }
  }

  const [sha, shortSha, committedAt, subject] = chosenLine.split('|');
  const [, , firstCommittedAt] = logLines[logLines.length - 1].split('|');

  return {
    lastCommitSha: shortSha,
    lastCommitFullSha: sha,
    lastCommitAt: committedAt,
    lastCommitSubject: subject || '',
    firstCommitAt: firstCommittedAt || committedAt,
  };
}

function resolvePluginRepo(pluginId, cfg) {
  const localCandidate = path.join(os.homedir(), 'projects', pluginId);
  if (fs.existsSync(path.join(localCandidate, '.git'))) {
    try {
      execFileSync('git', ['rev-parse', '--verify', `refs/tags/${cfg.tag}^{commit}`], {
        cwd: localCandidate,
        stdio: 'pipe',
      });
      return { repoDir: localCandidate, cleanup: () => {} };
    } catch {
      // Fall through to temporary clone if local repo lacks the tag
    }
  }

  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), `plugin-sync-${pluginId}-`));
  const repoUrl = `https://github.com/${cfg.repo}.git`;
  execFileSync('git', ['clone', '--quiet', '--branch', cfg.tag, repoUrl, tmpDir], {
    stdio: 'inherit',
  });
  return {
    repoDir: tmpDir,
    cleanup: () => fs.rmSync(tmpDir, { recursive: true, force: true }),
  };
}

export function syncPlugins() {
  if (!fs.existsSync(PLUGINS_JSON_PATH)) {
    throw new Error(`[Fail-Fast] Missing ${PLUGINS_JSON_PATH}`);
  }
  const pluginsConfig = JSON.parse(fs.readFileSync(PLUGINS_JSON_PATH, 'utf8'));
  fs.mkdirSync(PLUGINS_DIR, { recursive: true });

  for (const [pluginId, cfg] of Object.entries(pluginsConfig)) {
    if (!cfg.repo || !cfg.tag || !cfg.category) {
      throw new Error(`[Fail-Fast] Plugin "${pluginId}" in data/plugins.json is missing repo, tag, or category`);
    }

    const { repoDir, cleanup } = resolvePluginRepo(pluginId, cfg);
    try {
      const tagSha = execFileSync('git', ['rev-parse', '--verify', `refs/tags/${cfg.tag}^{commit}`], {
        cwd: repoDir,
        encoding: 'utf8',
      }).trim();

      const rawPluginJson = execFileSync('git', ['show', `${tagSha}:plugin.json`], {
        cwd: repoDir,
        encoding: 'utf8',
      });
      const pluginManifest = JSON.parse(rawPluginJson);
      const expectedTag = `v${pluginManifest.version}`;
      if (cfg.tag !== expectedTag) {
        throw new Error(
          `[Fail-Fast] Tag mismatch for plugin "${pluginId}": data/plugins.json specifies "${cfg.tag}", but plugin.json at that tag has version "${pluginManifest.version}" (expected "${expectedTag}")`
        );
      }

      const treeFiles = execFileSync('git', ['ls-tree', '-r', '--name-only', tagSha], {
        cwd: repoDir,
        encoding: 'utf8',
      })
        .trim()
        .split('\n')
        .filter(Boolean);

      const destPluginDir = path.join(PLUGINS_DIR, pluginId);
      fs.rmSync(destPluginDir, { recursive: true, force: true });
      fs.mkdirSync(destPluginDir, { recursive: true });

      const repoUrl = `https://github.com/${cfg.repo}`;
      const skillIds = [];

      for (const relPath of treeFiles) {
        if (!shouldVendorPath(relPath)) continue;

        const fileBuffer = execFileSync('git', ['show', `${tagSha}:${relPath}`], {
          cwd: repoDir,
          maxBuffer: 20 * 1024 * 1024,
        });
        const destFilePath = path.join(destPluginDir, relPath);
        fs.mkdirSync(path.dirname(destFilePath), { recursive: true });

        if (/^skills\/[^/]+\/SKILL\.md$/.test(relPath)) {
          const skillFolder = relPath.split('/')[1];
          skillIds.push(skillFolder);
          const normalized = injectSkillProvenance(fileBuffer.toString('utf8'), repoUrl, pluginId);
          fs.writeFileSync(destFilePath, normalized, 'utf8');
        } else {
          fs.writeFileSync(destFilePath, fileBuffer);
        }
      }

      const skillsHistory = {};
      for (const skillId of skillIds.sort()) {
        skillsHistory[skillId] = extractGitHistoryAtTag(
          repoDir,
          tagSha,
          `skills/${skillId}/SKILL.md`
        );
      }

      const upstreamHistory = {
        pluginId,
        repo: cfg.repo,
        tag: cfg.tag,
        tagCommitSha: tagSha,
        plugin: extractGitHistoryAtTag(repoDir, tagSha, null),
        skills: skillsHistory,
      };

      fs.writeFileSync(
        path.join(destPluginDir, '.upstream-history.json'),
        JSON.stringify(upstreamHistory, null, 2) + '\n',
        'utf8'
      );

      console.log(
        `✅ Synced plugin "${pluginId}" @ ${cfg.tag} (${tagSha.slice(0, 7)}) -> plugins/${pluginId}/ (${skillIds.length} bundled skills: ${skillIds.join(', ')})`
      );
    } finally {
      cleanup();
    }
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  syncPlugins();
}
