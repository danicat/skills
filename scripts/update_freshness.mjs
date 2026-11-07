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

const CATEGORIES = ['game-dev', 'media', 'coding', 'workflows', 'writing', 'analytics'];
const PARAMS_TOML_PATH = path.join(ROOT_DIR, 'config', '_default', 'params.toml');
const METRICS_PATH = path.join(ROOT_DIR, 'data', 'metrics_snapshot.json');
const CURATION_PATH = path.join(ROOT_DIR, 'data', 'curation.json');
const OUTPUT_PATH = path.join(ROOT_DIR, 'data', 'freshness.json');

export function classifyTier(score) {
  if (score === null || score === undefined) {
    return { tier: 'new', label: 'New', emoji: '🌱', half: 'new' };
  }
  if (score >= 90) {
    return { tier: 'mint', label: 'Mint', emoji: '✨', half: 'fresh' };
  }
  if (score >= 70) {
    return { tier: 'fresh', label: 'Fresh', emoji: '🌿', half: 'fresh' };
  }
  if (score >= 50) {
    return { tier: 'stale', label: 'Stale', emoji: '🕸️', half: 'fresh' };
  }
  if (score >= 25) {
    return { tier: 'spoiled', label: 'Spoiled', emoji: '🤢', half: 'danger' };
  }
  return { tier: 'rotten', label: 'Rotten', emoji: '🦠', half: 'danger' };
}

const commitModifiedSkillsCount = new Map();
function getModifiedSkillsCount(sha) {
  if (commitModifiedSkillsCount.has(sha)) {
    return commitModifiedSkillsCount.get(sha);
  }
  const out = execFileSync(
    'git',
    ['show', '--name-status', '--format=', sha],
    { cwd: ROOT_DIR, encoding: 'utf8' }
  )
    .trim()
    .split('\n')
    .filter(Boolean);

  const modifiedSkills = new Set();
  for (const line of out) {
    const parts = line.split(/\t+/);
    const status = parts[0];
    const file = parts[parts.length - 1];
    if (status.startsWith('A')) continue;
    const match = file.match(/^(game-dev|media|coding|workflows|traits|agents|writing|analytics|standards)\/([^/]+)\//);
    if (match) {
      modifiedSkills.add(match[2]);
    } else if (/^([^/.]+)\/(SKILL\.md|scripts|references)/.test(file)) {
      modifiedSkills.add(file.split('/')[0]);
    }
  }
  commitModifiedSkillsCount.set(sha, modifiedSkills.size);
  return modifiedSkills.size;
}

function isSubstantiveSkillCommit(sha, subject, skillId, relSkillDir, isInitialCommit, ignoredCommits) {
  if (isInitialCommit) return true;
  if (ignoredCommits.has(sha.slice(0, 7)) || ignoredCommits.has(sha)) return false;

  const lowerSubj = subject.toLowerCase();
  const mentionsSkill =
    lowerSubj.includes(skillId.toLowerCase()) ||
    (relSkillDir.startsWith('game-dev/') && lowerSubj.includes('game-dev'));

  const bulkCount = getModifiedSkillsCount(sha);
  if (bulkCount >= 10 && !mentionsSkill) return false;

  if (/^(chore|docs|style|ci)(\(|:)/.test(lowerSubj) && bulkCount >= 5 && !mentionsSkill) {
    return false;
  }

  const diff = execFileSync(
    'git',
    ['show', '-M', '--format=', sha, '--', relSkillDir, `traits/${skillId}`, `agents/${skillId}`, `coding/${skillId}`, `standards/${skillId}`, skillId],
    { cwd: ROOT_DIR, encoding: 'utf8' }
  );
  const changedLines = diff
    .split('\n')
    .filter((l) => (l.startsWith('+') && !l.startsWith('+++')) || (l.startsWith('-') && !l.startsWith('---')));

  const substantiveLines = changedLines.filter((l) => {
    const line = l.slice(1).trim();
    if (!line || line === '---') return false;
    if (/^(name|category|tags|author|license|catalog|canonical|version):/.test(line)) return false;
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

function getGitHistoryStrict(relSkillDir, skillId, curation) {
  const targetMdPath = resolveCommittedSkillPath(`${relSkillDir}/SKILL.md`);
  const logLines = execFileSync(
    'git',
    ['log', '--follow', '--format=%H|%h|%aI|%s', '--', targetMdPath],
    { cwd: ROOT_DIR, encoding: 'utf8' }
  )
    .trim()
    .split('\n')
    .filter(Boolean);

  if (logLines.length === 0) {
    throw new Error(`[Fail-Fast] No git commit history found for ${relSkillDir}/SKILL.md. Commit the skill first.`);
  }

  const ignoredCommits = new Set(curation?.ignoredCommits || []);
  let chosenLine = logLines[logLines.length - 1];
  for (let i = 0; i < logLines.length; i++) {
    const [fullSha, , , subj] = logLines[i].split('|');
    const isInitial = i === logLines.length - 1;
    if (isSubstantiveSkillCommit(fullSha, subj || '', skillId, relSkillDir, isInitial, ignoredCommits)) {
      chosenLine = logLines[i];
      break;
    }
  }

  const [sha, shortSha, committedAt, subject] = chosenLine.split('|');
  const [, , firstCommittedAt] = logLines[logLines.length - 1].split('|');

  const nowMs = Date.now();
  const lastMs = new Date(committedAt).getTime();
  const firstMs = new Date(firstCommittedAt || committedAt).getTime();

  const ageDays = Math.max(0, Number(((nowMs - lastMs) / 86_400_000).toFixed(2)));
  const plantedDaysAgo = Math.max(0, Number(((nowMs - firstMs) / 86_400_000).toFixed(2)));

  return {
    lastCommitSha: shortSha,
    lastCommitFullSha: sha,
    lastCommitAt: committedAt,
    lastCommitSubject: subject || '',
    firstCommitAt: firstCommittedAt || committedAt,
    ageDays,
    plantedDaysAgo,
    isNew: plantedDaysAgo <= 14,
  };
}

function readFirebaseConfig() {
  const toml = fs.readFileSync(PARAMS_TOML_PATH, 'utf8');
  const apiKeyMatch = toml.match(/apiKey\s*=\s*"([^"]+)"/);
  const projectIdMatch = toml.match(/projectId\s*=\s*"([^"]+)"/);
  if (!apiKeyMatch || !projectIdMatch) {
    throw new Error('[Fail-Fast] Missing [firebase] apiKey or projectId in config/_default/params.toml');
  }
  return { apiKey: apiKeyMatch[1], projectId: projectIdMatch[1] };
}

async function fetchLiveFirestoreSkillsMap() {
  const { apiKey, projectId } = readFirebaseConfig();
  const url = `https://firestore.googleapis.com/v1/projects/${encodeURIComponent(projectId)}/databases/(default)/documents/skills?pageSize=300&key=${encodeURIComponent(apiKey)}`;
  const res = await fetch(url, {
    headers: {
      Referer: 'https://skills.danicat.dev/',
    },
  });
  if (!res.ok) {
    throw new Error(`[Fail-Fast] Firestore skills fetch failed with HTTP ${res.status}`);
  }
  const data = await res.json();
  const bySkill = {};
  const parseIntField = (fieldObj) => {
    if (!fieldObj) return 0;
    const raw = fieldObj.integerValue !== undefined ? fieldObj.integerValue : fieldObj.doubleValue;
    return Math.max(0, Number.parseInt(raw || '0', 10) || 0);
  };

  for (const doc of data.documents || []) {
    const docId = (doc.name || '').split('/').pop() || '';
    const f = doc.fields || {};
    const rawSkill = f.skill?.stringValue || docId.replace(/^(game-dev|media|coding|workflows|traits|agents|writing|analytics|standards|plugins)-/, '');
    const sId = String(rawSkill || '').toLowerCase();
    if (!sId) continue;
    if (!bySkill[sId]) {
      bySkill[sId] = {
        likes: 0,
        views: 0,
        copies: 0,
        lastUpdated: null,
      };
    }
    bySkill[sId].likes += parseIntField(f.likes);
    bySkill[sId].views += parseIntField(f.views);
    bySkill[sId].copies += parseIntField(f.copies);
    if (f.lastUpdated?.timestampValue) {
      bySkill[sId].lastUpdated = f.lastUpdated.timestampValue;
    }
  }

  return bySkill;
}

function hydrateGitTimestamps(rawGit) {
  const nowMs = Date.now();
  const lastMs = new Date(rawGit.lastCommitAt).getTime();
  const firstMs = new Date(rawGit.firstCommitAt || rawGit.lastCommitAt).getTime();
  const ageDays = Math.max(0, Number(((nowMs - lastMs) / 86_400_000).toFixed(2)));
  const plantedDaysAgo = Math.max(0, Number(((nowMs - firstMs) / 86_400_000).toFixed(2)));
  return {
    ...rawGit,
    ageDays,
    plantedDaysAgo,
    isNew: plantedDaysAgo <= 14,
  };
}

async function fetchSkillsShTelemetry(skillId, repo = 'danicat/skills') {
  const detailUrl = `https://www.skills.sh/${repo}/${skillId}`;
  const auditUrl = `https://skills.sh/api/v1/skills/audit/${repo}/${skillId}`;

  const [detailRes, auditRes] = await Promise.all([
    fetch(detailUrl, { headers: { 'User-Agent': 'skills.danicat.dev-freshness-harvester/1.0' } }),
    fetch(auditUrl, { headers: { 'User-Agent': 'skills.danicat.dev-freshness-harvester/1.0' } }),
  ]);

  if (detailRes.status >= 500) {
    throw new Error(`[Fail-Fast] skills.sh returned HTTP ${detailRes.status} for ${detailUrl}`);
  }

  let installs = 0;
  let weeklyInstalls = [0, 0, 0, 0, 0, 0, 0, 0];
  let indexedOnSkillsSh = false;

  if (detailRes.status === 200) {
    const html = await detailRes.text();
    const isSoft404 =
      html.includes('name="robots" content="noindex, follow"') &&
      html.includes('404: This page could not be found');
    if (!isSoft404) {
      indexedOnSkillsSh = true;
      const totalMatch = html.match(/Installs<\/span><\/div><div[^>]*>([^<]+)<\/div>/);
      const ldMatch = html.match(/userInteractionCount["']?\s*:\s*(\d+)/);
      if (totalMatch) {
        const raw = totalMatch[1].trim().replace(/,/g, '');
        if (/^\d+$/.test(raw)) {
          installs = Number.parseInt(raw, 10);
        }
      } else if (ldMatch) {
        installs = Number(ldMatch[1]);
      }

      const flightMatch = html.match(/\\"values\\":\[([0-9,]+)\]/);
      const ariaMatch = html.match(/Weekly installs:\s*([0-9,\s]+)/i);
      const rawWeekly = flightMatch ? flightMatch[1] : ariaMatch ? ariaMatch[1] : null;
      if (rawWeekly) {
        const parsed = rawWeekly
          .split(',')
          .map((n) => Number.parseInt(n.trim(), 10))
          .filter((n) => !Number.isNaN(n));
        if (parsed.length === 8) {
          weeklyInstalls = parsed;
        }
      }
    }
  }

  let securityAudits = {};
  if (auditRes.status === 200) {
    const rawAudit = await auditRes.json();
    const auditsObj = rawAudit.audits || rawAudit || {};
    for (const [partner, val] of Object.entries(auditsObj)) {
      if (val && typeof val === 'object' && val.status) {
        const partnerKey = val.partner || partner;
        securityAudits[partnerKey] = {
          status: val.status,
          riskLevel: val.riskLevel || val.status.toUpperCase(),
          alerts: val.alerts ?? 0,
        };
      }
    }
  }

  return {
    indexedOnSkillsSh,
    installs,
    weeklyInstalls,
    securityAudits,
  };
}

function computeFreshnessMetrics({ git, skillsSh, curation }) {
  // 1. Substantive Git Recency U in [0, 1] with 45-day half-life (80% weight)
  const uRaw = Math.pow(0.5, git.ageDays / 45);
  const updateFreshness = Math.round(100 * uRaw);
  const vitalityPoints = Math.round(80 * uRaw);

  // 2. npx skills Installs (20% weight)
  const rawW = skillsSh.weeklyInstalls || [0, 0, 0, 0, 0, 0, 0, 0];
  const npxAllTime = Number(skillsSh.installs || 0);

  // Gate 0: Newly added skill without proven user activity yet -> 🌱 New
  const isUnproven = git.plantedDaysAgo <= 14 && npxAllTime <= 2;

  if (isUnproven) {
    const tierInfo = classifyTier(null);
    return {
      score: null,
      sortScore: 80,
      isUnproven: true,
      tier: tierInfo.tier,
      tierLabel: tierInfo.label,
      tierEmoji: tierInfo.emoji,
      half: tierInfo.half,
      updateFreshness,
      usageFreshness: 0,
      vitalityPoints: 0,
      adoptionBonusPoints: 0,
      trendRatio: 0,
      trendLabel: 'Unproven',
      securityPenalty: 0,
    };
  }

  // Raw 8-week trend from skills.sh
  const hist5Wk = (rawW[0] + rawW[1] + rawW[2] + rawW[3] + rawW[4]) / 5;
  const recent3Wk = (rawW[5] + rawW[6] + rawW[7]) / 3;
  const trendRatio = Number(((recent3Wk + 0.25) / (hist5Wk + 0.25)).toFixed(2));

  let trendLabel = 'Stable';
  if (trendRatio >= 1.25) {
    trendLabel = 'Growing';
  } else if (trendRatio >= 0.75) {
    trendLabel = 'Stable';
  } else if (trendRatio >= 0.35) {
    trendLabel = 'Decaying';
  } else {
    trendLabel = 'Flatlined';
  }

  // 20% weight: log-normalized installs against a target benchmark of 25 installs
  const iRaw = Math.min(1.0, Math.log10(1 + npxAllTime) / Math.log10(1 + 25));
  const usageFreshness = Math.round(100 * iRaw);
  const adoptionBonusPoints = Math.round(20 * iRaw);

  // 3. Security Penalty
  let securityPenalty = 0;
  const audits = skillsSh.securityAudits || {};
  const hasOverride = Boolean(curation?.auditOverride);

  if (!hasOverride) {
    for (const a of Object.values(audits)) {
      const risk = String(a.riskLevel || '').toUpperCase();
      if (a.status === 'fail' || risk === 'CRITICAL') {
        securityPenalty += 25;
      } else if (risk === 'HIGH') {
        securityPenalty += 15;
      }
    }
  }

  const score = Math.max(0, Math.min(100, vitalityPoints + adoptionBonusPoints - securityPenalty));
  const tierInfo = classifyTier(score);

  return {
    score,
    sortScore: score,
    isUnproven: false,
    tier: tierInfo.tier,
    tierLabel: tierInfo.label,
    tierEmoji: tierInfo.emoji,
    half: tierInfo.half,
    updateFreshness,
    usageFreshness,
    vitalityPoints,
    adoptionBonusPoints,
    trendRatio,
    trendLabel,
    securityPenalty,
  };
}

async function main() {
  console.log('✨ Harvesting Skill Freshness (Git 80% + npx skills 20%)...\n');

  const existingSnapshot = fs.existsSync(METRICS_PATH)
    ? JSON.parse(fs.readFileSync(METRICS_PATH, 'utf8'))
    : {};
  const liveFirestore = await fetchLiveFirestoreSkillsMap();
  const curationMap = fs.existsSync(CURATION_PATH)
    ? JSON.parse(fs.readFileSync(CURATION_PATH, 'utf8'))
    : {};

  // Merge live Firestore into metrics_snapshot.json
  const updatedSnapshot = { ...existingSnapshot };
  for (const [sId, data] of Object.entries(liveFirestore)) {
    const prev = updatedSnapshot[sId] || {};
    updatedSnapshot[sId] = {
      likes: Math.max(Number(prev.likes || 0), data.likes),
      views: Math.max(Number(prev.views || 0), data.views),
      copies: Math.max(Number(prev.copies || 0), data.copies),
      lastUpdated: data.lastUpdated || prev.lastUpdated || null,
    };
  }
  fs.writeFileSync(METRICS_PATH, JSON.stringify(updatedSnapshot, null, 2) + '\n', 'utf8');

  const skillEntries = [];
  for (const cat of CATEGORIES) {
    const catDir = path.join(ROOT_DIR, cat);
    if (!fs.existsSync(catDir)) continue;
    for (const folder of fs.readdirSync(catDir).sort()) {
      const skillMdPath = path.join(catDir, folder, 'SKILL.md');
      if (fs.existsSync(skillMdPath)) {
        skillEntries.push({
          category: cat,
          skillId: folder,
          displayName: folder,
          url: `/${cat}/${folder}/`,
          repo: 'danicat/skills',
          relDir: `${cat}/${folder}`,
        });
      }
    }
  }

  const result = {};
  for (const entry of skillEntries) {
    const curation = curationMap[entry.skillId] || null;
    const git = getGitHistoryStrict(entry.relDir, entry.skillId, curation);
    const firestore = updatedSnapshot[entry.skillId] || {
      likes: 0,
      views: 0,
      copies: 0,
    };
    const skillsSh = await fetchSkillsShTelemetry(entry.skillId, entry.repo);

    const metrics = computeFreshnessMetrics({ git, skillsSh, curation });

    const scanners = Object.values(skillsSh.securityAudits || {});
    const passedCount = scanners.filter((s) => s.status === 'pass').length;
    const warnCount = scanners.filter((s) => s.status === 'warn').length;
    const failCount = scanners.filter((s) => s.status === 'fail').length;

    let defaultSecurityNote = 'All active security scanners passed with zero alerts.';
    if (!skillsSh.indexedOnSkillsSh || scanners.length === 0) {
      defaultSecurityNote = 'Newly published skill awaiting initial upstream skills.sh scanner pass.';
    } else if (warnCount > 0 && failCount === 0) {
      defaultSecurityNote = 'Static scanner flagged local CLI execution documentation; Gen Trust Hub and Socket report 0 supply-chain alerts.';
    }

    result[entry.skillId] = {
      id: entry.skillId,
      displayName: entry.displayName,
      url: entry.url,
      repo: entry.repo,
      pluginId: entry.pluginId || null,
      category: entry.category,
      score: metrics.score,
      sortScore: metrics.sortScore,
      isUnproven: metrics.isUnproven,
      tier: metrics.tier,
      tierLabel: metrics.tierLabel,
      tierEmoji: metrics.tierEmoji,
      half: metrics.half,
      isNew: git.isNew || metrics.isUnproven,
      updateFreshness: metrics.updateFreshness,
      usageFreshness: metrics.usageFreshness,
      vitalityPoints: metrics.vitalityPoints,
      adoptionBonusPoints: metrics.adoptionBonusPoints,
      trendRatio: metrics.trendRatio,
      trendLabel: metrics.trendLabel,
      securityPenalty: metrics.securityPenalty,
      lastCommitSha: git.lastCommitSha,
      lastCommitAt: git.lastCommitAt,
      lastCommitDate: git.lastCommitAt.slice(0, 10),
      ageDays: git.ageDays,
      plantedDate: git.firstCommitAt.slice(0, 10),
      installs: skillsSh.installs,
      weeklyInstalls: skillsSh.weeklyInstalls,
      currentWeeklyInstalls: skillsSh.weeklyInstalls[7] || 0,
      likes: Number(firestore.likes || 0),
      views: Number(firestore.views || 0),
      copies: Number(firestore.copies || 0),
      securityAudits: skillsSh.securityAudits,
      scannerSummary: {
        total: scanners.length,
        pass: passedCount,
        warn: warnCount,
        fail: failCount,
      },
      securityNote: curation?.securityNote || defaultSecurityNote,
      editorialNote: curation?.editorialNote || '',
    };

    const scoreDisplay = metrics.score === null ? 'NEW' : `${String(metrics.score).padStart(3)}%`;
    console.log(
      `  ${metrics.tierEmoji} ${entry.skillId.padEnd(22)} ${scoreDisplay} (${metrics.tierLabel.padEnd(7)}) | Git=${String(metrics.updateFreshness).padStart(3)}% (${metrics.vitalityPoints}pts) | npx=${String(skillsSh.installs).padStart(2)} (${metrics.adoptionBonusPoints}pts) | last=${git.lastCommitAt.slice(0, 10)} (${String(Math.round(git.ageDays)).padStart(3)}d)`
    );
  }

  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(result, null, 2) + '\n', 'utf8');
  console.log(`\n✅ Wrote ${Object.keys(result).length} skills to ${path.relative(ROOT_DIR, OUTPUT_PATH)}`);
}

main().catch((err) => {
  console.error('\n[FRESHNESS HARVEST FAILED]', err);
  process.exit(1);
});
