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
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');

export const CATEGORIES = ['game-dev', 'media', 'coding', 'workflows', 'writing', 'analytics'];
export const HISTORICAL_CATEGORIES = [
  'game-dev',
  'media',
  'coding',
  'workflows',
  'traits',
  'agents',
  'writing',
  'analytics',
  'standards',
];
export const GRACE_DAYS = 30;
export const HALF_LIFE_DAYS = 90;
export const MIN_SUBSTANTIVE_LINES = 4;

const IGNORED_DIRS = new Set(['__pycache__', '.git', 'node_modules']);
const IGNORED_FILES = new Set(['.DS_Store']);
const TEST_FILE_PATTERN = /^test_|_test\.(go|py|js|mjs|ts)$|\.(test|spec)\.(js|mjs|ts)$/;
const METADATA_LINE_PATTERN = /^(name|category|tags|author|license|catalog|canonical|version|metadata):/;
const LICENSE_HEADER_PATTERN =
  /^(#|\/\/|\*|<!--|-->)\s*(Copyright 202\d|SPDX-License|Licensed under|you may not use|http:\/\/www\.apache\.org|Unless required|WITHOUT WARRANTIES|See the License|limitations under)/i;

export function classifyTier(score) {
  const numeric = Number(score);
  if (numeric >= 85) {
    return { tier: 'current', label: 'Current' };
  }
  if (numeric >= 60) {
    return { tier: 'active', label: 'Active' };
  }
  if (numeric >= 35) {
    return { tier: 'aging', label: 'Aging' };
  }
  return { tier: 'outdated', label: 'Outdated' };
}

export function computeFreshnessScore(ageDays) {
  const clamped = Math.max(0, Number(ageDays) || 0);
  if (clamped <= GRACE_DAYS) {
    return 100;
  }
  const decayed = 100 * Math.pow(0.5, (clamped - GRACE_DAYS) / HALF_LIFE_DAYS);
  return Math.max(0, Math.min(100, Math.round(decayed)));
}

export function countSubstantiveLinesFromDiff(diffText) {
  if (!diffText) {
    return 0;
  }
  const changedLines = diffText
    .split('\n')
    .filter((line) => (line.startsWith('+') && !line.startsWith('+++')) || (line.startsWith('-') && !line.startsWith('---')));

  let count = 0;
  for (const rawLine of changedLines) {
    const trimmed = rawLine.slice(1).trim();
    if (!trimmed || trimmed === '---') {
      continue;
    }
    if (METADATA_LINE_PATTERN.test(trimmed)) {
      continue;
    }
    if (LICENSE_HEADER_PATTERN.test(trimmed)) {
      continue;
    }
    count++;
  }
  return count;
}

function resolveCommittedSkillPath(relFilePath) {
  const porcelain = execFileSync('git', ['status', '--porcelain'], { cwd: ROOT_DIR, encoding: 'utf8' });
  for (const line of porcelain.split('\n')) {
    const match = line.match(/^R.\s+(.+?)\s+->\s+(.+)$/);
    if (match && match[2].trim() === relFilePath) {
      return match[1].trim();
    }
  }
  return relFilePath;
}

function parseGitLogLines(rawOutput) {
  const entries = [];
  for (const line of rawOutput.trim().split('\n')) {
    if (!line) {
      continue;
    }
    const [sha, shortSha, committedAt, ...subjectParts] = line.split('|');
    if (!sha || !shortSha || !committedAt) {
      continue;
    }
    entries.push({
      sha,
      shortSha,
      committedAt,
      timeMs: new Date(committedAt).getTime(),
      subject: subjectParts.join('|'),
    });
  }
  return entries;
}

function buildSkillPathspecs(relSkillDir, skillId) {
  const candidates = [relSkillDir, ...HISTORICAL_CATEGORIES.map((cat) => `${cat}/${skillId}`), skillId];
  return [...new Set(candidates)];
}

export function getSkillGitHistory(relSkillDir, skillId) {
  const pathspecs = buildSkillPathspecs(relSkillDir, skillId);
  const committedSkillMdPath = resolveCommittedSkillPath(`${relSkillDir}/SKILL.md`);

  const folderLogRaw = execFileSync(
    'git',
    ['log', '--format=%H|%h|%aI|%s', '--', ...pathspecs],
    { cwd: ROOT_DIR, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 }
  );
  const followLogRaw = execFileSync(
    'git',
    ['log', '--follow', '--format=%H|%h|%aI|%s', '--', committedSkillMdPath],
    { cwd: ROOT_DIR, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 }
  );

  const bySha = new Map();
  let order = 0;
  for (const item of [...parseGitLogLines(folderLogRaw), ...parseGitLogLines(followLogRaw)]) {
    if (!bySha.has(item.sha)) {
      bySha.set(item.sha, { ...item, order: order++ });
    }
  }

  const commits = Array.from(bySha.values()).sort((a, b) => b.timeMs - a.timeMs || a.order - b.order);
  if (commits.length === 0) {
    throw new Error(`[Fail-Fast] No git commit history found for ${relSkillDir}/SKILL.md. Commit the skill first.`);
  }

  let latestSubstantive = null;
  let substantiveCommits = 0;

  for (let i = 0; i < commits.length; i++) {
    const commit = commits[i];
    const isInitialCommit = i === commits.length - 1;
    const diff = execFileSync(
      'git',
      ['show', '-M', '--format=', commit.sha, '--', ...pathspecs],
      { cwd: ROOT_DIR, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 }
    );
    const diffLines = countSubstantiveLinesFromDiff(diff);
    if (isInitialCommit || diffLines >= MIN_SUBSTANTIVE_LINES) {
      substantiveCommits++;
      if (!latestSubstantive) {
        latestSubstantive = { ...commit, diffLines };
      }
    }
  }

  const initialCommit = commits[commits.length - 1];
  const nowMs = Date.now();
  const lastMs = latestSubstantive.timeMs;
  const firstMs = initialCommit.timeMs;

  const ageDays = Math.max(0, Number(((nowMs - lastMs) / 86_400_000).toFixed(2)));
  const effectiveDecayDays = Math.max(0, Number(Math.max(0, ageDays - GRACE_DAYS).toFixed(2)));
  const createdDaysAgo = Math.max(0, Number(((nowMs - firstMs) / 86_400_000).toFixed(2)));

  return {
    lastCommitSha: latestSubstantive.shortSha,
    lastCommitFullSha: latestSubstantive.sha,
    lastCommitAt: latestSubstantive.committedAt,
    lastCommitDate: latestSubstantive.committedAt.slice(0, 10),
    lastCommitSubject: latestSubstantive.subject,
    lastDiffLines: latestSubstantive.diffLines,
    createdAt: initialCommit.committedAt,
    createdDate: initialCommit.committedAt.slice(0, 10),
    createdDaysAgo,
    isNew: createdDaysAgo <= 14,
    ageDays,
    effectiveDecayDays,
    substantiveCommits,
    totalCommits: commits.length,
  };
}

function listSkillFilesRecursive(absDir, relPrefix = '') {
  const entries = fs.readdirSync(absDir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name));
  const files = [];
  for (const entry of entries) {
    if (IGNORED_DIRS.has(entry.name) || IGNORED_FILES.has(entry.name)) {
      continue;
    }
    const absPath = path.join(absDir, entry.name);
    const relPath = relPrefix ? `${relPrefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      files.push(...listSkillFilesRecursive(absPath, relPath));
    } else if (entry.isFile()) {
      if (entry.name.endsWith('.pyc') || entry.name.endsWith('.pyo')) {
        continue;
      }
      files.push(relPath);
    }
  }
  return files;
}

export function inspectSkillBundle(relSkillDir) {
  const absDir = path.join(ROOT_DIR, relSkillDir);
  const skillMdPath = path.join(absDir, 'SKILL.md');
  if (!fs.existsSync(skillMdPath)) {
    throw new Error(`[Fail-Fast] Missing SKILL.md at ${skillMdPath}`);
  }

  const rawSkillMd = fs.readFileSync(skillMdPath, 'utf8');
  const fmMatch = rawSkillMd.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fmMatch) {
    throw new Error(`[Fail-Fast] Missing YAML frontmatter in ${relSkillDir}/SKILL.md`);
  }
  const versionMatch = fmMatch[1].match(/^\s*version:\s*["']?([^"'\r\n]+)["']?/m);
  if (!versionMatch || !versionMatch[1].trim()) {
    throw new Error(`[Fail-Fast] Missing metadata.version in ${relSkillDir}/SKILL.md`);
  }
  const version = versionMatch[1].trim();

  const files = listSkillFilesRecursive(absDir);
  const fileCount = files.length;
  const distributionType = fileCount > 1 ? 'archive' : 'skill-md';

  let scriptCount = 0;
  let testCount = 0;
  let referenceCount = 0;

  for (const relPath of files) {
    const base = path.basename(relPath);
    if (relPath.startsWith('scripts/')) {
      if (base === 'go.mod' || base === 'go.sum') {
        continue;
      }
      if (TEST_FILE_PATTERN.test(base)) {
        testCount++;
      } else {
        scriptCount++;
      }
    } else if (/^(references|assets|examples|resources)\//.test(relPath)) {
      referenceCount++;
    }
  }

  return {
    version,
    distributionType,
    fileCount,
    scriptCount,
    testCount,
    referenceCount,
    hasTests: testCount > 0,
  };
}

export function buildFreshnessCatalog() {
  const result = {};

  for (const cat of CATEGORIES) {
    const catDir = path.join(ROOT_DIR, cat);
    if (!fs.existsSync(catDir)) {
      throw new Error(`[Fail-Fast] Missing category directory: ${cat}`);
    }

    for (const folder of fs.readdirSync(catDir).sort()) {
      const relSkillDir = `${cat}/${folder}`;
      const skillMdPath = path.join(ROOT_DIR, relSkillDir, 'SKILL.md');
      if (!fs.existsSync(skillMdPath)) {
        continue;
      }

      const git = getSkillGitHistory(relSkillDir, folder);
      const bundle = inspectSkillBundle(relSkillDir);
      const score = computeFreshnessScore(git.ageDays);
      const tierInfo = classifyTier(score);

      result[folder] = {
        id: folder,
        displayName: folder,
        url: `/${cat}/${folder}/`,
        repo: 'danicat/skills',
        category: cat,
        version: bundle.version,
        distributionType: bundle.distributionType,
        score,
        sortScore: score,
        tier: tierInfo.tier,
        tierLabel: tierInfo.label,
        isNew: git.isNew,
        graceDays: GRACE_DAYS,
        halfLifeDays: HALF_LIFE_DAYS,
        ageDays: git.ageDays,
        effectiveDecayDays: git.effectiveDecayDays,
        lastCommitSha: git.lastCommitSha,
        lastCommitFullSha: git.lastCommitFullSha,
        lastCommitAt: git.lastCommitAt,
        lastCommitDate: git.lastCommitDate,
        lastCommitSubject: git.lastCommitSubject,
        lastDiffLines: git.lastDiffLines,
        createdAt: git.createdAt,
        createdDate: git.createdDate,
        substantiveCommits: git.substantiveCommits,
        totalCommits: git.totalCommits,
        fileCount: bundle.fileCount,
        scriptCount: bundle.scriptCount,
        testCount: bundle.testCount,
        referenceCount: bundle.referenceCount,
        hasTests: bundle.hasTests,
      };
    }
  }

  return result;
}

function main() {
  console.log(`Harvesting pure Git freshness (${GRACE_DAYS}d grace + ${HALF_LIFE_DAYS}d half-life)...\n`);
  const catalog = buildFreshnessCatalog();
  const outputPath = path.join(ROOT_DIR, 'data', 'freshness.json');
  fs.writeFileSync(outputPath, JSON.stringify(catalog, null, 2) + '\n', 'utf8');

  for (const entry of Object.values(catalog)) {
    const scoreText = `${String(entry.score).padStart(3)}%`;
    console.log(
      `  ${entry.id.padEnd(22)} ${scoreText} (${entry.tierLabel.padEnd(8)}) | age=${String(Math.round(entry.ageDays)).padStart(3)}d | diff=${String(entry.lastDiffLines).padStart(4)}L | commits=${String(entry.substantiveCommits).padStart(2)}/${String(entry.totalCommits).padStart(2)} | last=${entry.lastCommitDate} (${entry.lastCommitSha})`
    );
  }

  console.log(`\nWrote ${Object.keys(catalog).length} skills to ${path.relative(ROOT_DIR, outputPath)}`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main();
}
