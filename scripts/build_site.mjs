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

const CATEGORIES = [
  { id: 'game-dev', name: 'Game Development', emoji: '🕹️', description: '2D game architecture, Ebitengine v2, chiptune DSP, and procedural graphics in Go.' },
  { id: 'media', name: 'Generative Media', emoji: '🎨', description: 'Lyria 3 music synthesis and Nano Banana conversational image generation.' },
  { id: 'coding', name: 'Coding & Tooling', emoji: '💻', description: 'SemVer, broken window hygiene, AST-aware Go developer tooling, and Python uv workflows.' },
  { id: 'agents', name: 'Agents & Meta-Tooling', emoji: '🤖', description: 'A2UI streaming protocol, multi-agent swarm coding, and skill optimizer.' },
  { id: 'writing', name: 'Technical Writing', emoji: '✍️', description: 'Google Developers Blog style guide, Vale linters, and Google Codelabs tutorial authoring.' },
  { id: 'standards', name: 'Engineering Standards', emoji: '📐', description: 'Architecture Decision Records (ADRs) and Request for Comments (RFC) frameworks.' },
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
  console.log('Building skills catalog with Blowfish visual identity...');

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
  fs.writeFileSync(path.join(SITE_DIR, 'llms.txt'), llmsTxt);
  fs.writeFileSync(path.join(ROOT_DIR, 'llms.txt'), llmsTxt);

  // 3. llms-full.txt
  let llmsFullTxt = `# danicat/skills (Full Instructions Catalog)\n\n> Complete collection of all Agent Skills.\n\n---\n\n`;
  for (const s of skills) {
    llmsFullTxt += `# Skill: ${s.name} (${s.category})\n\n> ${s.description}\n\n`;
    llmsFullTxt += `**Source**: ${s.url}\n**Install**: \`${s.installCommand}\`\n\n`;
    llmsFullTxt += `## Instructions\n\n${s.body}\n\n---\n\n`;
  }
  fs.writeFileSync(path.join(SITE_DIR, 'llms-full.txt'), llmsFullTxt);

  // 4. catalog.json
  const catalog = {
    $schema: 'https://agentskills.io/schema.json',
    name: 'danicat/skills',
    title: 'Daniela Petruzalek Agent Skills Catalog',
    url: DOMAIN,
    repository: REPO_URL,
    totalSkills: skills.length,
    updatedAt: new Date().toISOString(),
    categories: CATEGORIES,
    skills: skills.map(({ body, ...rest }) => rest),
  };
  const catalogJson = JSON.stringify(catalog, null, 2);
  fs.writeFileSync(path.join(SITE_DIR, 'catalog.json'), catalogJson);
  fs.writeFileSync(path.join(ROOT_DIR, 'catalog.json'), catalogJson);

  // 5. HTML Index with Blowfish theme alignment
  const html = `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agent Skills · danicat.dev</title>
  <meta name="description" content="A curated collection of specialized Agent Skills by Daniela Petruzalek for coding, game dev, AI media, technical writing, and standards.">
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
          <a href="/llms.txt" class="nav-link accent">llms.txt</a>
          <a href="/catalog.json" class="nav-link">JSON</a>
          <button id="themeToggle" class="theme-toggle-btn" aria-label="Toggle light/dark theme" title="Toggle theme">
            <span id="themeIcon">☀️</span>
          </button>
        </div>
      </nav>
    </header>

    <div class="hero">
      <h1>Agent Skills Collection</h1>
      <p>Modular, spec-compliant capability modules for AI coding assistants and autonomous agents across 2D game development, media generation, architecture standards, and engineering workflows.</p>
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
      <p><a href="${BLOG_URL}">← Back to danicat.dev</a> · <a href="${REPO_URL}">GitHub Repository</a> · <a href="/llms.txt">llms.txt</a></p>
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
        const orig = btn.textContent;
        btn.textContent = '✓';
        btn.style.color = 'var(--green)';
        setTimeout(() => {
          btn.textContent = orig;
          btn.style.color = '';
        }, 1500);
      });
    }
  </script>
</body>
</html>`;

  fs.writeFileSync(path.join(SITE_DIR, 'index.html'), html);
  console.log(`Site build complete! Generated ${skills.length} skills in _site/ with Blowfish styling.`);
}

build().catch(err => {
  console.error(err);
  process.exit(1);
});
