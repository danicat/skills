import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SITE_DIR = path.resolve(ROOT_DIR, '_site');

const DOMAIN = 'https://skills.danicat.dev';
const REPO_URL = 'https://github.com/danicat/skills';
const BLOG_URL = 'https://danicat.dev';
const GA_MEASUREMENT_ID = 'G-8RHDQGEGZ2';

const CATEGORIES = [
  { id: 'game-dev', name: 'Game Development', emoji: '🕹️', description: '2D games in Go with Ebitengine, chiptune audio, and procedural graphics.' },
  { id: 'media', name: 'Generative Media', emoji: '🎨', description: 'Lyria 3 music synthesis and Nano Banana image editing.' },
  { id: 'coding', name: 'Coding & Tooling', emoji: '💻', description: 'Semantic versioning, repository hygiene, GoDoctor, and Python uv workflows.' },
  { id: 'agents', name: 'Agents & Meta-Tooling', emoji: '🤖', description: 'A2UI streaming protocol, multi-agent swarms, and skill optimizer.' },
  { id: 'writing', name: 'Technical Writing', emoji: '✍️', description: 'Google Developers Blog style guide and Google Codelabs tutorials.' },
  { id: 'standards', name: 'Engineering Standards', emoji: '📐', description: 'Architecture Decision Records (ADRs) and Request for Comments (RFCs).' },
];

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

  for (const line of lines) {
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

async function build() {
  console.log('Building skills catalog with sitemap.xml, robots.txt, and SEO...');

  if (fs.existsSync(SITE_DIR)) {
    fs.rmSync(SITE_DIR, { recursive: true, force: true });
  }
  fs.mkdirSync(SITE_DIR, { recursive: true });

  const skills = [];

  for (const cat of CATEGORIES) {
    const catDir = path.join(ROOT_DIR, cat.id);
    if (!fs.existsSync(catDir)) continue;

    const skillFolders = fs.readdirSync(catDir, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);

    for (const skillFolder of skillFolders) {
      const skillPath = path.join(catDir, skillFolder, 'SKILL.md');
      if (!fs.existsSync(skillPath)) continue;

      const raw = fs.readFileSync(skillPath, 'utf8');
      const { data, body } = parseFrontmatter(raw);

      const skillRecord = {
        name: data.name || skillFolder,
        category: cat.id,
        categoryName: cat.name,
        categoryEmoji: cat.emoji,
        description: data.description || '',
        license: data.license || 'Apache-2.0',
        installCommand: `npx skills install github.com/danicat/skills/${cat.id}/${skillFolder}`,
        url: `${DOMAIN}/${cat.id}/${skillFolder}/SKILL.md`,
        githubUrl: `${REPO_URL}/tree/main/${cat.id}/${skillFolder}`,
        relativePath: `${cat.id}/${skillFolder}/SKILL.md`,
        body: body.trim(),
      };

      skills.push(skillRecord);
      copyRecursive(path.join(catDir, skillFolder), path.join(SITE_DIR, cat.id, skillFolder));
    }
  }

  const todayIso = new Date().toISOString().split('T')[0];

  // 1. CNAME
  fs.writeFileSync(path.join(SITE_DIR, 'CNAME'), 'skills.danicat.dev\n');

  // 2. Root SKILL.md (Catalog Gateway)
  const rootSkillPath = path.join(ROOT_DIR, 'SKILL.md');
  if (fs.existsSync(rootSkillPath)) {
    fs.copyFileSync(rootSkillPath, path.join(SITE_DIR, 'SKILL.md'));
  }

  // 3. llms.txt
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
  fs.writeFileSync(path.join(SITE_DIR, 'llms.txt'), llmsTxt);
  fs.writeFileSync(path.join(ROOT_DIR, 'llms.txt'), llmsTxt);

  // 4. llms-full.txt
  let llmsFullTxt = `# danicat/skills (Full Instructions Catalog)\n\n> Complete collection of all Agent Skills.\n\n---\n\n`;
  for (const s of skills) {
    llmsFullTxt += `# Skill: ${s.name} (${s.category})\n\n> ${s.description}\n\n`;
    llmsFullTxt += `**Source**: ${s.url}\n**Install**: \`${s.installCommand}\`\n\n`;
    llmsFullTxt += `## Instructions\n\n${s.body}\n\n---\n\n`;
  }
  fs.writeFileSync(path.join(SITE_DIR, 'llms-full.txt'), llmsFullTxt);

  // 5. catalog.json
  const catalog = {
    $schema: 'https://agentskills.io/schema.json',
    name: 'danicat/skills',
    title: 'Daniela Petruzalek Agent Skills Catalog',
    url: DOMAIN,
    repository: REPO_URL,
    totalSkills: skills.length,
    updatedAt: new Date().toISOString(),
    categories: CATEGORIES,
    gateway: {
      name: 'catalog',
      description: 'Dynamic search and loader for all skills in this repository.',
      url: `${DOMAIN}/SKILL.md`,
      installCommand: 'npx skills install github.com/danicat/skills',
    },
    skills: skills.map(({ body, ...rest }) => rest),
  };
  const catalogJson = JSON.stringify(catalog, null, 2);
  fs.writeFileSync(path.join(SITE_DIR, 'catalog.json'), catalogJson);
  fs.writeFileSync(path.join(ROOT_DIR, 'catalog.json'), catalogJson);

  // 6. sitemap.xml
  let sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
  sitemapXml += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/SKILL.md</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/llms.txt</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  for (const s of skills) {
    sitemapXml += `  <url>\n    <loc>${s.url}</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n`;
  }
  sitemapXml += `</urlset>\n`;
  fs.writeFileSync(path.join(SITE_DIR, 'sitemap.xml'), sitemapXml);

  // 7. robots.txt
  const robotsTxt = `User-agent: *\nAllow: /\n\nSitemap: ${DOMAIN}/sitemap.xml\n`;
  fs.writeFileSync(path.join(SITE_DIR, 'robots.txt'), robotsTxt);

  // 8. HTML Index with Google Analytics, SEO, and Blowfish styling
  const html = `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agent Skills · Daniela Petruzalek (danicat.dev)</title>
  <meta name="description" content="A curated collection of Agent Skills for 2D Go games, Python tooling, engineering standards, technical writing, and generative media.">
  <link rel="canonical" href="${DOMAIN}/">

  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '${GA_MEASUREMENT_ID}');
  </script>

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="${DOMAIN}/">
  <meta property="og:title" content="Agent Skills · Daniela Petruzalek">
  <meta property="og:description" content="A curated collection of Agent Skills for 2D Go games, Python tooling, engineering standards, technical writing, and generative media.">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Agent Skills · Daniela Petruzalek">
  <meta name="twitter:description" content="A curated collection of Agent Skills for 2D Go games, Python tooling, engineering standards, technical writing, and generative media.">

  <link rel="icon" type="image/png" sizes="32x32" href="${BLOG_URL}/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="${BLOG_URL}/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="${BLOG_URL}/apple-touch-icon.png">
  <style>
    :root {
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      
      /* Blowfish Light Palette */
      --bg: #ffffff;
      --bg-alt: #f8fafc;
      --surface: #ffffff;
      --surface-hover: #f1f5f9;
      --border: #e2e8f0;
      --border-hover: #cbd5e1;
      --text: #334155;
      --text-heading: #0f172a;
      --text-muted: #64748b;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-subtle: #eff6ff;
      --primary-border: #bfdbfe;
      --code-bg: #f8fafc;
      --code-border: #e2e8f0;
      --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
      --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
      --badge-bg: #f1f5f9;
      --green: #16a34a;
      --hero-banner-bg: #f8fafc;
      --hero-banner-border: #e2e8f0;
    }

    html[data-theme="dark"] {
      /* Blowfish Dark Palette */
      --bg: #0f172a;
      --bg-alt: #1e293b;
      --surface: #1e293b;
      --surface-hover: #273549;
      --border: #334155;
      --border-hover: #475569;
      --text: #cbd5e1;
      --text-heading: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #60a5fa;
      --primary-hover: #93c5fd;
      --primary-subtle: rgba(59, 130, 246, 0.12);
      --primary-border: rgba(96, 165, 250, 0.3);
      --code-bg: #090d16;
      --code-border: #1e293b;
      --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
      --shadow-hover: 0 10px 20px -3px rgba(0, 0, 0, 0.5);
      --badge-bg: #273549;
      --green: #4ade80;
      --hero-banner-bg: rgba(30, 41, 59, 0.7);
      --hero-banner-border: #334155;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.65;
      padding: 0 1.5rem 5rem;
      transition: background-color 0.2s ease, color 0.2s ease;
      -webkit-font-smoothing: antialiased;
    }

    .container {
      max-width: 1160px;
      margin: 0 auto;
    }

    /* Blowfish-aligned Header */
    header {
      padding: 1.5rem 0 2.5rem;
      border-bottom: 1px solid var(--border);
      margin-bottom: 2.5rem;
    }

    .nav-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .brand-wrap {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      text-decoration: none;
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-heading);
      letter-spacing: -0.01em;
    }

    .brand-wrap:hover .brand-skills {
      color: var(--primary);
    }

    .brand-sep {
      color: var(--text-muted);
      font-weight: 300;
    }

    .brand-skills {
      color: var(--primary);
      transition: color 0.15s ease;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }

    .nav-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.92rem;
      font-weight: 500;
      padding: 0.4rem 0.75rem;
      border-radius: 6px;
      transition: all 0.15s ease;
    }

    .nav-link:hover {
      color: var(--text-heading);
      background-color: var(--surface-hover);
    }

    .nav-link.accent {
      color: var(--primary);
      border: 1px solid var(--primary-border);
      background: var(--primary-subtle);
    }

    .theme-toggle-btn {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-muted);
      cursor: pointer;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }

    .theme-toggle-btn:hover {
      color: var(--text-heading);
      border-color: var(--border-hover);
      background: var(--surface-hover);
    }

    /* Hero */
    .hero {
      margin-bottom: 2.5rem;
    }

    .hero h1 {
      font-size: 2.5rem;
      font-weight: 800;
      color: var(--text-heading);
      letter-spacing: -0.03em;
      line-height: 1.2;
      margin-bottom: 0.75rem;
    }

    .hero p {
      font-size: 1.15rem;
      color: var(--text-muted);
      max-width: 800px;
    }

    /* Gateway Banner */
    .gateway-banner {
      background: var(--hero-banner-bg);
      border: 1px solid var(--hero-banner-border);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin-top: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      box-shadow: var(--shadow);
    }

    .gateway-banner-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .gateway-title-wrap {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 600;
      color: var(--text-heading);
      font-size: 0.95rem;
    }

    .gateway-link {
      font-size: 0.85rem;
      color: var(--primary);
      text-decoration: none;
      font-weight: 500;
    }

    .gateway-link:hover {
      text-decoration: underline;
    }

    .gateway-install-box {
      display: flex;
      align-items: center;
      background: var(--code-bg);
      border: 1px solid var(--code-border);
      border-radius: 8px;
      padding: 0.55rem 0.85rem;
      font-family: var(--font-mono);
      font-size: 0.88rem;
      color: var(--text-heading);
    }

    .gateway-cmd {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      padding-right: 0.5rem;
    }

    .gateway-copy-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-heading);
      cursor: pointer;
      padding: 0.3rem 0.65rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.15s ease;
    }

    .gateway-copy-btn:hover {
      border-color: var(--primary);
      color: var(--primary);
    }

    .gateway-caption {
      font-size: 0.82rem;
      color: var(--text-muted);
    }

    /* Search & Filters */
    .search-filter-section {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      margin-bottom: 3rem;
    }

    .search-input-wrapper {
      position: relative;
      width: 100%;
    }

    .search-input-wrapper input {
      width: 100%;
      padding: 0.9rem 1.25rem 0.9rem 2.85rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      color: var(--text-heading);
      font-size: 1rem;
      outline: none;
      box-shadow: var(--shadow);
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .search-input-wrapper input:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-subtle);
    }

    .search-icon {
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
    }

    .category-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .pill-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.4rem 0.95rem;
      border-radius: 9999px;
      font-size: 0.88rem;
      font-weight: 500;
      cursor: pointer;
      box-shadow: var(--shadow);
      transition: all 0.15s ease;
    }

    .pill-btn:hover {
      color: var(--text-heading);
      border-color: var(--border-hover);
      transform: translateY(-1px);
    }

    .pill-btn.active {
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
      font-weight: 600;
    }

    /* Grid & Cards */
    .skills-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.5rem;
    }

    .skill-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: var(--shadow);
      transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
    }

    .skill-card:hover {
      border-color: var(--primary-border);
      transform: translateY(-3px);
      box-shadow: var(--shadow-hover);
    }

    .card-top {
      margin-bottom: 1.25rem;
    }

    .card-title-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.85rem;
      gap: 0.5rem;
    }

    .skill-name-link {
      font-size: 1.2rem;
      font-weight: 700;
      color: var(--text-heading);
      text-decoration: none;
      letter-spacing: -0.01em;
    }

    .skill-name-link:hover {
      color: var(--primary);
    }

    .cat-badge {
      font-size: 0.76rem;
      font-weight: 600;
      padding: 0.2rem 0.55rem;
      border-radius: 9999px;
      background: var(--badge-bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      white-space: nowrap;
    }

    .skill-description {
      font-size: 0.92rem;
      color: var(--text);
      line-height: 1.55;
    }

    .card-bottom {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border);
    }

    .cmd-box {
      display: flex;
      align-items: center;
      background: var(--code-bg);
      border: 1px solid var(--code-border);
      border-radius: 8px;
      padding: 0.45rem 0.75rem;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    .cmd-text {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
      padding-right: 0.5rem;
    }

    .copy-button {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 0.2rem 0.35rem;
      border-radius: 4px;
      font-size: 0.85rem;
      transition: color 0.15s ease, transform 0.1s ease;
    }

    .copy-button:hover {
      color: var(--text-heading);
      transform: scale(1.1);
    }

    .card-links {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      font-weight: 500;
    }

    .card-links a {
      color: var(--primary);
      text-decoration: none;
      transition: color 0.15s ease;
    }

    .card-links a:hover {
      color: var(--primary-hover);
      text-decoration: underline;
    }

    .no-results {
      grid-column: 1 / -1;
      text-align: center;
      padding: 4rem 1rem;
      color: var(--text-muted);
      font-size: 1.15rem;
    }

    /* Footer */
    footer {
      margin-top: 5rem;
      padding-top: 2rem;
      border-top: 1px solid var(--border);
      text-align: center;
      font-size: 0.9rem;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    footer a {
      color: var(--primary);
      text-decoration: none;
      font-weight: 500;
    }

    footer a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <nav class="nav-bar">
        <a href="${BLOG_URL}" class="brand-wrap">
          <span>danicat.dev</span>
          <span class="brand-sep">/</span>
          <span class="brand-skills">skills</span>
        </a>
        <div class="nav-links">
          <a href="${BLOG_URL}/posts/" class="nav-link">Posts</a>
          <a href="${BLOG_URL}/events/" class="nav-link">Events</a>
          <a href="${BLOG_URL}/codelabs/" class="nav-link">Codelabs</a>
          <a href="${BLOG_URL}/about/" class="nav-link">About</a>
          <a href="${REPO_URL}" target="_blank" rel="noopener" class="nav-link">GitHub ↗</a>
          <a href="/SKILL.md" class="nav-link">SKILL.md</a>
          <a href="/llms.txt" class="nav-link accent">llms.txt</a>
          <a href="/catalog.json" class="nav-link">JSON</a>
          <button id="themeToggle" class="theme-toggle-btn" aria-label="Toggle light/dark theme" title="Toggle theme">
            <span id="themeIcon">☀️</span>
          </button>
        </div>
      </nav>
    </header>

    <div class="hero">
      <h1>Agent Skills</h1>
      <p>A collection of focused skills for AI coding agents. Covers 2D Go games, Python tooling, engineering standards, technical writing, and generative media.</p>

      <div class="gateway-banner">
        <div class="gateway-banner-header">
          <div class="gateway-title-wrap">
            <span>⚡</span>
            <span>Get the complete catalog</span>
          </div>
          <a href="/SKILL.md" class="gateway-link">View gateway SKILL.md →</a>
        </div>
        <div class="gateway-install-box">
          <span class="gateway-cmd">npx skills install github.com/danicat/skills</span>
          <button class="gateway-copy-btn" onclick="copyInstall('npx skills install github.com/danicat/skills', this)" title="Copy install command">
            <span>📋</span> Copy
          </button>
        </div>
        <p class="gateway-caption">Adds an on-demand router to your coding agent so it can fetch any skill in this collection as you work.</p>
      </div>
    </div>

    <section class="search-filter-section">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Search skills by name, keywords, or capabilities... (Press '/' to focus)" autofocus>
      </div>
      <div class="category-pills" id="categoryFilters">
        <button class="pill-btn active" data-cat="all">All (${skills.length})</button>
        ${CATEGORIES.map(c => `<button class="pill-btn" data-cat="${c.id}">${c.emoji} ${c.name} (${skills.filter(s => s.category === c.id).length})</button>`).join('\n        ')}
      </div>
    </section>

    <main>
      <div class="skills-grid" id="skillsGrid">
        ${skills.map(s => `
        <div class="skill-card" data-category="${s.category}" data-name="${s.name.toLowerCase()}" data-desc="${s.description.toLowerCase().replace(/"/g, '&quot;')}">
          <div class="card-top">
            <div class="card-title-row">
              <a href="/${s.relativePath}" class="skill-name-link">${s.name}</a>
              <span class="cat-badge">${s.categoryEmoji} ${s.categoryName}</span>
            </div>
            <p class="skill-description">${s.description}</p>
          </div>
          <div class="card-bottom">
            <div class="cmd-box">
              <span class="cmd-text">${s.installCommand}</span>
              <button class="copy-button" onclick="copyInstall('${s.installCommand}', this)" title="Copy install command">📋</button>
            </div>
            <div class="card-links">
              <a href="/${s.relativePath}">View SKILL.md</a>
              <a href="${s.githubUrl}" target="_blank" rel="noopener">Source code ↗</a>
            </div>
          </div>
        </div>`).join('')}
      </div>
    </main>

    <footer>
      <p>© Daniela Petruzalek · Open source under Apache-2.0</p>
      <p><a href="${BLOG_URL}">← Back to danicat.dev</a> · <a href="${REPO_URL}">GitHub Repository</a> · <a href="/llms.txt">llms.txt</a> · <a href="/sitemap.xml">sitemap.xml</a></p>
    </footer>
  </div>

  <script>
    // Theme Management aligned with blowfish & localStorage
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlEl = document.documentElement;

    function applyTheme(theme) {
      htmlEl.setAttribute('data-theme', theme);
      themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
      localStorage.setItem('appearance', theme);
    }

    // Initialize Theme
    const savedTheme = localStorage.getItem('appearance') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    applyTheme(savedTheme);

    themeToggle.addEventListener('click', () => {
      const current = htmlEl.getAttribute('data-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });

    // Search and Filter Logic
    const searchInput = document.getElementById('searchInput');
    const pillButtons = document.querySelectorAll('.pill-btn');
    const cards = document.querySelectorAll('.skill-card');
    const grid = document.getElementById('skillsGrid');

    let activeCategory = 'all';

    function filterSkills() {
      const query = searchInput.value.toLowerCase().trim();
      let count = 0;

      cards.forEach(card => {
        const cat = card.getAttribute('data-category');
        const name = card.getAttribute('data-name');
        const desc = card.getAttribute('data-desc');

        const matchesCat = activeCategory === 'all' || cat === activeCategory;
        const matchesQuery = !query || name.includes(query) || desc.includes(query) || cat.includes(query);

        if (matchesCat && matchesQuery) {
          card.style.display = 'flex';
          count++;
        } else {
          card.style.display = 'none';
        }
      });

      let noRes = document.getElementById('noResults');
      if (count === 0) {
        if (!noRes) {
          noRes = document.createElement('div');
          noRes.id = 'noResults';
          noRes.className = 'no-results';
          noRes.textContent = 'No skills matching your criteria.';
          grid.appendChild(noRes);
        }
      } else if (noRes) {
        noRes.remove();
      }
    }

    searchInput.addEventListener('input', filterSkills);

    pillButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        pillButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeCategory = btn.getAttribute('data-cat');
        filterSkills();
      });
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    });

    function copyInstall(cmd, btn) {
      navigator.clipboard.writeText(cmd).then(() => {
        const orig = btn.innerHTML;
        btn.innerHTML = '<span>✓</span> Copied';
        btn.style.borderColor = 'var(--green)';
        btn.style.color = 'var(--green)';
        setTimeout(() => {
          btn.innerHTML = orig;
          btn.style.borderColor = '';
          btn.style.color = '';
        }, 1500);
      });
    }
  </script>
</body>
</html>`;

  fs.writeFileSync(path.join(SITE_DIR, 'index.html'), html);
  console.log(`Site build complete! Generated ${skills.length} skills, sitemap.xml, and robots.txt in _site/.`);
}

build().catch(err => {
  console.error(err);
  process.exit(1);
});
