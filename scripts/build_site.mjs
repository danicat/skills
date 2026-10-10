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
import crypto from 'crypto';
import { execFileSync } from 'child_process';
import { fileURLToPath } from 'url';
import { runAudit } from './qa_audit.mjs';
import { fixA2uiLinks } from './fix_a2ui_links.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SITE_DIR = path.resolve(ROOT_DIR, '_site');

const SUB_DOMAIN = 'https://skills.danicat.dev';
const REPO_URL = 'https://github.com/danicat/skills';

const CATEGORIES = [
  { id: 'game-dev', name: 'Games', emoji: '🕹️', description: 'Design and build high-performance 2D games in Go using Ebitengine v2 with procedural art, chiptune DSP sound synthesis, sprite animation, and GDD specifications.' },
  { id: 'media', name: 'GenAI', emoji: '🎨', description: 'Synthesize high-fidelity stereo audio with Google Lyria 3 and generate conversational visuals using Nano Banana multimodal image models.' },
  { id: 'coding', name: 'Software Engineering', emoji: '💻', description: 'Automate semantic versioning, Go AST refactoring with GoDoctor MCP, Python uv environments, ADRs, RFCs, and Google open-source compliance.' },
  { id: 'agents', name: 'Agents', emoji: '🤖', description: 'Orchestrate multi-agent swarms, coordinate Double-Diamond workflows, communicate across sessions, and author verified Agent Skills.' },
  { id: 'writing', name: 'Writing', emoji: '✍️', description: 'Author publication-grade engineering blogs, Inverted Pyramid documentation, anti-slop copy, technical SEO/GEO, and developer social copy.' },
  { id: 'analytics', name: 'Analytics', emoji: '📊', description: 'Ingest Google Analytics 4, Google Search Console, and Buffer metrics into local SQLite warehouses for deep SQL querying.' },
];

function loadAuthoritativeIdentity() {
  const identityPath = path.resolve(ROOT_DIR, 'data/identity.json');
  if (!fs.existsSync(identityPath)) {
    throw new Error(`CRITICAL: Authoritative identity file missing at ${identityPath}`);
  }
  let data;
  try {
    data = JSON.parse(fs.readFileSync(identityPath, 'utf8'));
  } catch (e) {
    throw new Error(`CRITICAL: Failed to parse ${identityPath}: ${e.message}`);
  }
  if (!data.author || !data.publisher) {
    throw new Error(`CRITICAL: Identity file at ${identityPath} is missing required 'author' or 'publisher' fields`);
  }
  return data;
}

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { data: {}, body: content };
  const rawYaml = match[1];
  const body = match[2];
  const data = {};

  const lines = rawYaml.split(/\r?\n/);
  let currentKey = null;
  let inFolded = false;
  let foldedLines = [];
  let inMetadata = false;

  for (const line of lines) {
    if (line.startsWith('metadata:')) {
      data.metadata = {};
      inMetadata = true;
      inFolded = false;
      continue;
    }

    if (inMetadata && line.startsWith('  ')) {
      const subMatch = line.trim().match(/^([a-zA-Z0-9_-]+):\s*(.*)$/);
      if (subMatch) {
        data.metadata[subMatch[1]] = subMatch[2].replace(/^["']|["']$/g, '').trim();
      }
      continue;
    } else if (inMetadata && !line.startsWith('  ')) {
      inMetadata = false;
    }

    const keyValMatch = line.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/);
    if (keyValMatch && !line.startsWith('  ')) {
      if (currentKey && inFolded) {
        data[currentKey] = foldedLines.join(' ').trim();
        inFolded = false;
        foldedLines = [];
      }
      currentKey = keyValMatch[1];
      const val = keyValMatch[2].trim();
      if (val === '>' || val === '|' || val === '>-' || val === '|-') {
        inFolded = true;
      } else {
        data[currentKey] = val.replace(/^["']|["']$/g, '');
      }
    } else if (inFolded && line.startsWith('  ')) {
      foldedLines.push(line.trim());
    }
  }
  if (currentKey && inFolded) {
    data[currentKey] = foldedLines.join(' ').trim();
  }
  return { data, body };
}

function copyRecursive(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  if (isDirectory) {
    fs.mkdirSync(dest, { recursive: true });
    for (const child of fs.readdirSync(src)) {
      copyRecursive(path.join(src, child), path.join(dest, child));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

function discoverBundledResources(skillDir) {
  const resources = [];
  const folders = ['references', 'scripts', 'assets', 'evals'];
  for (const f of folders) {
    const full = path.join(skillDir, f);
    if (!fs.existsSync(full)) continue;
    function walk(d, rel) {
      for (const item of fs.readdirSync(d)) {
        const itemFull = path.join(d, item);
        const itemRel = path.join(rel, item);
        const st = fs.statSync(itemFull);
        if (st.isDirectory()) {
          walk(itemFull, itemRel);
        } else {
          resources.push({
            type: f,
            relPath: itemRel,
            name: item,
            isMarkdown: item.endsWith('.md'),
            sizeBytes: st.size
          });
        }
      }
    }
    walk(full, f);
  }
  return resources;
}

async function build() {
  console.log('Building skills.danicat.dev with Hugo + Blowfish, catalog.json, llms.txt, and QA audit...');

  loadAuthoritativeIdentity();
  fixA2uiLinks();

  const evalDir = path.join(ROOT_DIR, 'writing/seo-optimizer/evals/files');
  if (fs.existsSync(evalDir)) {
    const png1px = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=', 'base64');
    fs.writeFileSync(path.join(evalDir, 'diagram.png'), png1px);
    fs.writeFileSync(path.join(evalDir, 'mcp_architecture.png'), png1px);
  }

  if (fs.existsSync(SITE_DIR)) {
    fs.rmSync(SITE_DIR, { recursive: true, force: true });
  }
  fs.mkdirSync(SITE_DIR, { recursive: true });

  // Run Hugo build
  console.log('Executing: hugo --gc --minify --noBuildLock -d _site');
  execFileSync('hugo', ['--gc', '--minify', '--noBuildLock', '-d', SITE_DIR], {
    cwd: ROOT_DIR,
    stdio: 'inherit'
  });

  // Copy raw skill files byte-for-byte to preserve SHA-256 parity and companion assets
  const skills = [];
  const allReferencePages = [];

  for (const cat of CATEGORIES) {
    const catDir = path.join(ROOT_DIR, cat.id);
    if (!fs.existsSync(catDir)) continue;

    const skillFolders = fs.readdirSync(catDir, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);

    for (const skillFolder of skillFolders) {
      const skillDir = path.join(catDir, skillFolder);
      const skillPath = path.join(skillDir, 'SKILL.md');
      if (!fs.existsSync(skillPath)) continue;

      const raw = fs.readFileSync(skillPath, 'utf8');
      const { data, body } = parseFrontmatter(raw);

      const sha256 = crypto.createHash('sha256').update(raw).digest('hex');
      const tags = data.metadata?.tags ? data.metadata.tags.split(',').map(t => t.trim()).filter(Boolean) : [cat.id, skillFolder];
      const version = data.metadata?.version || '0.1.0';
      const author = data.metadata?.author || 'Daniela Petruzalek (daniela@danicat.dev)';
      const byteSize = Buffer.byteLength(raw, 'utf8');
      const tokenEstimate = Math.ceil(byteSize / 4);

      const skillRecord = {
        name: data.name || skillFolder,
        folder: skillFolder,
        category: cat.id,
        categoryName: cat.name,
        categoryEmoji: cat.emoji,
        description: data.description || '',
        license: data.license || 'Apache-2.0',
        author,
        version,
        digest: `sha256:${sha256}`,
        sha256,
        byteSize,
        tokenEstimate,
        tags,
        metadata: data.metadata || {},
        installCommand: `npx skills add danicat/skills --skill ${data.name || skillFolder} -y`,
        kungfuLoadCommand: `kungfu load ${data.name || skillFolder}`,
        kungfuLearnCommand: `kungfu learn ${data.name || skillFolder}`,
        url: `${SUB_DOMAIN}/${cat.id}/${skillFolder}/SKILL.md`,
        detailUrl: `${SUB_DOMAIN}/${cat.id}/${skillFolder}/`,
        githubUrl: `${REPO_URL}/tree/main/${cat.id}/${skillFolder}`,
        relativePath: `${cat.id}/${skillFolder}/SKILL.md`,
        body: body.trim(),
      };

      skills.push(skillRecord);

      // Copy raw files byte-for-byte into _site/<category>/<skillFolder>
      copyRecursive(skillDir, path.join(SITE_DIR, cat.id, skillFolder));

      // Verify raw SKILL.md SHA-256 parity in _site
      const copiedRaw = fs.readFileSync(path.join(SITE_DIR, cat.id, skillFolder, 'SKILL.md'), 'utf8');
      const copiedSha256 = crypto.createHash('sha256').update(copiedRaw).digest('hex');
      if (copiedSha256 !== sha256) {
        throw new Error(`CRITICAL: SHA-256 parity mismatch for _site/${cat.id}/${skillFolder}/SKILL.md`);
      }

      const resources = discoverBundledResources(skillDir);
      for (const res of resources) {
        if (res.isMarkdown) {
          const relNoExt = res.relPath.replace(/\.md$/, '');
          const slug = `${skillFolder}__${relNoExt.replace(/[^a-zA-Z0-9_-]/g, '__')}`.toLowerCase();
          const hugoCompanionDir = path.join(SITE_DIR, cat.id, slug);
          const hugoCompanionHtml = path.join(hugoCompanionDir, 'index.html');
          const outRefHtmlPath = path.join(SITE_DIR, cat.id, skillFolder, `${relNoExt}.html`);

          if (fs.existsSync(hugoCompanionHtml)) {
            fs.mkdirSync(path.dirname(outRefHtmlPath), { recursive: true });
            let htmlContent = fs.readFileSync(hugoCompanionHtml, 'utf8');
            const wrongRelUrl = `/${cat.id}/${slug}/`;
            const rightRelUrl = `/${cat.id}/${skillFolder}/${relNoExt}.html`;
            htmlContent = htmlContent.split(wrongRelUrl).join(rightRelUrl);
            fs.writeFileSync(outRefHtmlPath, htmlContent, 'utf8');
            fs.rmSync(hugoCompanionDir, { recursive: true, force: true });
          }

          if (!fs.existsSync(outRefHtmlPath)) {
            throw new Error(`CRITICAL: Expected Hugo-rendered companion page missing at ${outRefHtmlPath}`);
          }
          allReferencePages.push({
            url: `${skillRecord.detailUrl}${relNoExt}.html`,
            relPath: res.relPath,
            skill: skillRecord.name
          });
        }
      }
    }
  }

  // Ensure /assets/chibi_dani_oops.png is present in _site/assets/
  const oopsSrc = path.join(ROOT_DIR, 'assets/chibi_dani_oops.png');
  if (fs.existsSync(oopsSrc)) {
    copyRecursive(oopsSrc, path.join(SITE_DIR, 'assets/chibi_dani_oops.png'));
  }

  const todayIso = new Date().toISOString().split('T')[0];

  // 1. CNAME
  fs.writeFileSync(path.join(SITE_DIR, 'CNAME'), 'skills.danicat.dev\n');

  // 2. llms.txt
  let llmsTxt = `# danicat/skills\n\n> A curated collection of specialized Agent Skills for coding, game development, generative media, writing, and standards.\n\n`;
  for (const cat of CATEGORIES) {
    const catSkills = skills.filter(s => s.category === cat.id);
    if (catSkills.length === 0) continue;
    llmsTxt += `## ${cat.name}\n\n`;
    for (const s of catSkills) {
      llmsTxt += `- [${s.name}](${s.url}): ${s.description}\n`;
    }
    llmsTxt += `\n`;
  }
  llmsTxt += `## Optional\n\n`;
  llmsTxt += `- [Full Instructions Catalog](${SUB_DOMAIN}/llms-full.txt): Complete bundle of all ${skills.length} skill instructions in a single file for large-context models.\n`;
  llmsTxt += `- [Catalog Manifest](${SUB_DOMAIN}/catalog.json): Machine-readable catalog manifest with metadata, tags, and digests.\n`;
  fs.writeFileSync(path.join(SITE_DIR, 'llms.txt'), llmsTxt.trim() + '\n');
  fs.writeFileSync(path.join(ROOT_DIR, 'llms.txt'), llmsTxt.trim() + '\n');

  // 3. llms-full.txt
  let llmsFullTxt = `# danicat/skills (Full Instructions Catalog)\n\n> Complete collection of all Agent Skills.\n\n---\n\n`;
  for (const s of skills) {
    llmsFullTxt += `# Skill: ${s.name} (${s.category})\n\n> ${s.description}\n\n`;
    llmsFullTxt += `**Web Page**: ${s.detailUrl}\n**Source**: ${s.url}\n**Version**: ${s.version}\n**Digest**: ${s.digest}\n**Install**: \`${s.installCommand}\`\n\n`;
    llmsFullTxt += `## Instructions\n\n${s.body}\n\n---\n\n`;
  }
  fs.writeFileSync(path.join(SITE_DIR, 'llms-full.txt'), llmsFullTxt.trim() + '\n');

  // 4. Skills Catalog Manifest (catalog.json)
  const catalogManifest = {
    name: 'danicat/skills',
    title: 'Agent Skills',
    url: SUB_DOMAIN,
    repository: REPO_URL,
    totalSkills: skills.length,
    updatedAt: new Date().toISOString(),
    categories: CATEGORIES.map(c => ({
      id: c.id,
      name: c.name,
      emoji: c.emoji,
      description: c.description
    })),
    skills: skills.map(s => ({
      name: s.name,
      description: s.description,
      category: s.category,
      tags: s.tags,
      author: s.author,
      version: s.version,
      license: s.license,
      url: s.url,
      digest: s.digest
    }))
  };
  const catalogJson = JSON.stringify(catalogManifest, null, 2);

  fs.writeFileSync(path.join(SITE_DIR, 'catalog.json'), catalogJson);
  fs.writeFileSync(path.join(ROOT_DIR, 'catalog.json'), catalogJson);

  // 5. Clean canonical sitemap.xml (homepages + 30 canonical skill pages across en, pt-br, ja)
  let sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
  sitemapXml += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;
  sitemapXml += `  <url>\n    <loc>${SUB_DOMAIN}/</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${SUB_DOMAIN}/pt-br/</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${SUB_DOMAIN}/ja/</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  for (const s of skills) {
    sitemapXml += `  <url>\n    <loc>${s.detailUrl}</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.85</priority>\n  </url>\n`;
    sitemapXml += `  <url>\n    <loc>${SUB_DOMAIN}/pt-br/${s.category}/${s.folder}/</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n`;
    sitemapXml += `  <url>\n    <loc>${SUB_DOMAIN}/ja/${s.category}/${s.folder}/</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n`;
  }
  sitemapXml += `</urlset>\n`;
  fs.writeFileSync(path.join(SITE_DIR, 'sitemap.xml'), sitemapXml);

  // 6. robots.txt
  const robotsTxt = `User-agent: *\nAllow: /\n\nSitemap: ${SUB_DOMAIN}/sitemap.xml\n`;
  fs.writeFileSync(path.join(SITE_DIR, 'robots.txt'), robotsTxt);

  console.log(`Site build complete! Generated ${skills.length} skills detail pages, ${allReferencePages.length} companion reference pages, 404.html, sitemap.xml, robots.txt, and assets in _site/.`);

  const auditResult = runAudit();
  if (
    auditResult.htmlErrors.length > 0 ||
    auditResult.assetErrors.length > 0 ||
    auditResult.uiIssues.length > 0 ||
    auditResult.warnings.length > 0
  ) {
    throw new Error(
      `CRITICAL: QA Audit failed — htmlErrors=${auditResult.htmlErrors.length}, assetErrors=${auditResult.assetErrors.length}, uiIssues=${auditResult.uiIssues.length}, warnings=${auditResult.warnings.length}`
    );
  }
}

build().catch(err => {
  console.error(err);
  process.exit(1);
});
