import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import { runAudit } from './qa_audit.mjs';
import { fixA2uiLinks } from './fix_a2ui_links.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SITE_DIR = path.resolve(ROOT_DIR, '_site');

const DOMAIN = 'https://skills.danicat.dev';
const REPO_URL = 'https://github.com/danicat/skills';
const BLOG_URL = 'https://danicat.dev';
const GA_MEASUREMENT_ID = 'G-8RHDQGEGZ2';
const ENABLE_KUNGFU = process.env.ENABLE_KUNGFU === 'true' || false;

const CATEGORIES = [
  { id: 'game-dev', name: 'Game Development', emoji: '🕹️', description: 'Build high-performance 2D games in Go using Ebitengine v2 with procedural art, chiptune DSP sound synthesis, sprite animation, and GDD design.' },
  { id: 'media', name: 'Generative Media', emoji: '🎨', description: 'Synthesize 44.1 kHz stereo music with Google Lyria 3 and generate conversational visuals using Nano Banana multimodal image models.' },
  { id: 'coding', name: 'Coding & Tooling', emoji: '💻', description: 'Enforce semantic versioning, Go AST refactoring with GoDoctor MCP, Python uv workflows, polyglot GitHub search, and zero-debt hygiene.' },
  { id: 'agents', name: 'Agents & Meta-Tooling', emoji: '🤖', description: 'Orchestrate multi-agent swarms, implement Double-Diamond workflows, build A2UI streaming interfaces, and author verified Agent Skills.' },
  { id: 'writing', name: 'Technical Writing', emoji: '✍️', description: 'Author publication-grade engineering blogs, codelabs, Inverted Pyramid documentation, anti-slop copy, SEO metadata, and social analytics.' },
];

const SCHEMA_AUTHOR = {
  '@type': 'Person',
  '@id': 'https://danicat.dev/#person',
  'name': 'Daniela Petruzalek',
  'url': 'https://danicat.dev',
  'jobTitle': 'Staff Developer Advocate & Software Engineer',
  'sameAs': [
    'https://github.com/danicat',
    'https://twitter.com/danicat83',
    'https://linkedin.com/in/danicat',
    'https://bsky.app/profile/danicat.dev'
  ]
};

const SCHEMA_PUBLISHER = {
  '@type': 'Organization',
  '@id': `${DOMAIN}/#organization`,
  'name': 'danicat/skills',
  'url': DOMAIN,
  'logo': {
    '@type': 'ImageObject',
    'url': `${BLOG_URL}/apple-touch-icon.png`
  }
};

const GITHUB_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 496 512" width="18" height="18" fill="currentColor"><path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"/></svg>`;
const MOON_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="18" height="18" fill="currentColor"><path d="M32 256c0-123.8 100.3-224 223.8-224c11.36 0 29.7 1.668 40.9 3.746c9.616 1.777 11.75 14.63 3.279 19.44C245 86.5 211.2 144.6 211.2 207.8c0 109.7 99.71 193 208.3 172.3c9.561-1.805 16.28 9.324 10.11 16.95C387.9 448.6 324.8 480 255.8 480C132.1 480 32 379.6 32 256z"/></svg>`;
const SUN_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="18" height="18" fill="currentColor"><path d="M256 159.1c-53.02 0-95.1 42.98-95.1 95.1S202.1 351.1 256 351.1s95.1-42.98 95.1-95.1S309 159.1 256 159.1zM509.3 347L446.1 255.1l63.15-91.01c6.332-9.125 1.104-21.74-9.826-23.72l-109-19.7l-19.7-109c-1.975-10.93-14.59-16.16-23.72-9.824L256 65.89L164.1 2.736c-9.125-6.332-21.74-1.107-23.72 9.824L121.6 121.6L12.56 141.3C1.633 143.2-3.596 155.9 2.736 164.1L65.89 256l-63.15 91.01c-6.332 9.125-1.105 21.74 9.824 23.72l109 19.7l19.7 109c1.975 10.93 14.59 16.16 23.72 9.824L256 446.1l91.01 63.15c9.127 6.334 21.75 1.107 23.72-9.822l19.7-109l109-19.7C510.4 368.8 515.6 356.1 509.3 347zM256 383.1c-70.69 0-127.1-57.31-127.1-127.1c0-70.69 57.31-127.1 127.1-127.1s127.1 57.3 127.1 127.1C383.1 326.7 326.7 383.1 256 383.1z"/></svg>`;

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/<[^>]+>/g, '')
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-');
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

function parseInlineFormatting(text) {
  let res = escapeHtml(text);

  // Bold + Italic
  res = res.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');
  res = res.replace(/___([^_]+)___/g, '<strong><em>$1</em></strong>');

  // Bold
  res = res.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  res = res.replace(/__([^_]+)__/g, '<strong>$1</strong>');

  // Italic
  res = res.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  res = res.replace(/(^|[\s(])_([^_]+)_(?=[\s).,;!?]|$)/g, '$1<em>$2</em>');

  // Strikethrough
  res = res.replace(/~~([^~]+)~~/g, '<del>$1</del>');

  return res;
}

function parseInline(text) {
  if (!text) return '';

  const mathTokens = [];
  let s = text.replace(/\$\$([\s\S]*?)\$\$/g, (m, math) => {
    const token = `%%MATH_BLOCK_${mathTokens.length}%%`;
    mathTokens.push(`<span class="math-display">${escapeHtml(math)}</span>`);
    return token;
  });
  s = s.replace(/\$([^\$\n]+)\$/g, (m, math) => {
    const token = `%%MATH_BLOCK_${mathTokens.length}%%`;
    mathTokens.push(`<span class="math-inline">${escapeHtml(math)}</span>`);
    return token;
  });

  const codeTokens = [];
  s = s.replace(/`([^`]+)`/g, (m, code) => {
    const token = `%%INLINE_CODE_${codeTokens.length}%%`;
    codeTokens.push(`<code class="inline-code">${escapeHtml(code)}</code>`);
    return token;
  });

  const linkTokens = [];
  // Images first
  s = s.replace(/!\[(.*?)\]\((.*?)\)/g, (m, alt, src) => {
    const token = `%%LINK_TOKEN_${linkTokens.length}%%`;
    linkTokens.push(`<figure class="content-img"><img src="${escapeHtml(src)}" alt="${escapeHtml(alt)}" loading="lazy"><figcaption>${escapeHtml(alt)}</figcaption></figure>`);
    return token;
  });

  // Links
  s = s.replace(/\[(.*?)\]\((.*?)\)/g, (m, label, href) => {
    let finalHref = href;
    let isExternal = href.startsWith('http://') || href.startsWith('https://');
    if (!isExternal) {
      if (finalHref.includes('{{<') && finalHref.includes('ref')) {
        const match = finalHref.match(/ref\s+["']([^"']+)["']/);
        if (match) {
          finalHref = `https://danicat.dev${match[1].startsWith('/') ? '' : '/'}${match[1]}/`;
          isExternal = true;
        }
      } else {
        const parts = finalHref.split('#');
        const queryParts = parts[0].split('?');
        if (queryParts[0].endsWith('/SKILL.md')) {
          queryParts[0] = queryParts[0].replace(/\/SKILL\.md$/, '/');
          let newHref = queryParts.join('?');
          if (parts.length > 1) {
            newHref += '#' + parts.slice(1).join('#');
          }
          finalHref = newHref;
        } else if (queryParts[0] === 'SKILL.md') {
          queryParts[0] = './';
          let newHref = queryParts.join('?');
          if (parts.length > 1) {
            newHref += '#' + parts.slice(1).join('#');
          }
          finalHref = newHref;
        } else if (queryParts[0].endsWith('.md')) {
          queryParts[0] = queryParts[0].replace(/\.md$/, '.html');
          let newHref = queryParts.join('?');
          if (parts.length > 1) {
            newHref += '#' + parts.slice(1).join('#');
          }
          finalHref = newHref;
        }
      }
    }
    const token = `%%LINK_TOKEN_${linkTokens.length}%%`;
    if (isExternal) {
      linkTokens.push(`<a href="${escapeHtml(finalHref)}" target="_blank" rel="noopener noreferrer">${parseInlineFormatting(label)} <span class="ext-icon">↗</span></a>`);
    } else {
      linkTokens.push(`<a href="${escapeHtml(finalHref)}">${parseInlineFormatting(label)}</a>`);
    }
    return token;
  });

  // Apply formatting to remaining text
  s = parseInlineFormatting(s);

  // Restore links
  s = s.replace(/%%LINK_TOKEN_(\d+)%%/g, (m, idx) => linkTokens[parseInt(idx, 10)]);

  // Restore code
  s = s.replace(/%%INLINE_CODE_(\d+)%%/g, (m, idx) => codeTokens[parseInt(idx, 10)]);

  // Restore math
  s = s.replace(/%%MATH_BLOCK_(\d+)%%/g, (m, idx) => mathTokens[parseInt(idx, 10)]);

  return s;
}

function markdownToHtml(markdown, options = {}) {
  const isSubDocument = options.isSubDocument || false;
  const codeBlocks = [];
  let processed = markdown.replace(/```([a-zA-Z0-9_-]*)\r?\n([\s\S]*?)```/g, (match, lang, code) => {
    const id = `%%CODE_BLOCK_${codeBlocks.length}%%`;
    codeBlocks.push({ lang: lang.trim().toLowerCase(), code });
    return id;
  });

  const callouts = [];
  processed = processed.replace(/^>[ \t]*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*\r?\n((?:>[ \t]*.*(?:\r?\n|$))*)/gim, (match, type, content) => {
    const id = `%%CALLOUT_${callouts.length}%%`;
    const cleanLines = content
      .split(/\r?\n/)
      .map(line => line.replace(/^>[ \t]?/, ''))
      .join('\n')
      .trim();
    callouts.push({ type: type.toUpperCase(), content: cleanLines });
    return id + '\n\n';
  });

  const lines = processed.split(/\r?\n/);
  const out = [];
  const toc = [];

  const listStack = [];

  function closeAllLists() {
    while (listStack.length > 0) {
      const top = listStack.pop();
      if (top.inItem) {
        out.push('</li>');
      }
      out.push(`</${top.type}>`);
    }
  }

  function handleListItem(indent, type, rawText) {
    while (listStack.length > 0 && listStack[listStack.length - 1].indent > indent) {
      const top = listStack.pop();
      if (top.inItem) {
        out.push('</li>');
      }
      out.push(`</${top.type}>`);
    }

    if (listStack.length === 0 || indent > listStack[listStack.length - 1].indent) {
      listStack.push({ type, indent, inItem: true });
      out.push(`<${type} class="prose-${type}">`);
    } else {
      const current = listStack[listStack.length - 1];
      if (current.type !== type) {
        if (current.inItem) out.push('</li>');
        out.push(`</${current.type}>`);
        current.type = type;
        current.inItem = true;
        out.push(`<${type} class="prose-${type}">`);
      } else {
        if (current.inItem) {
          out.push('</li>');
        }
        current.inItem = true;
      }
    }

    let parsedItem = rawText;
    const taskMatch = parsedItem.match(/^\[([ xX])\]\s+(.*)$/);
    if (taskMatch) {
      const checked = taskMatch[1].toLowerCase() === 'x';
      parsedItem = `<input type="checkbox" disabled ${checked ? 'checked' : ''} class="task-check"> ${parseInline(taskMatch[2])}`;
      out.push(`<li class="task-list-item">${parsedItem}`);
    } else {
      out.push(`<li>${parseInline(parsedItem)}`);
    }
  }

  let inTable = false;
  let tableRows = [];
  let inBlockquote = false;
  let blockquoteLines = [];

  function closeTable() {
    if (inTable) {
      if (tableRows.length > 0) {
        out.push('<div class="table-wrap"><table class="prose-table">');
        const headerCells = tableRows[0];
        out.push('<thead><tr>');
        for (const cell of headerCells) {
          out.push(`<th>${parseInline(cell.trim())}</th>`);
        }
        out.push('</tr></thead>');

        if (tableRows.length > 1) {
          out.push('<tbody>');
          for (let i = 1; i < tableRows.length; i++) {
            out.push('<tr>');
            for (const cell of tableRows[i]) {
              out.push(`<td>${parseInline(cell.trim())}</td>`);
            }
            out.push('</tr>');
          }
          out.push('</tbody>');
        }
        out.push('</table></div>');
      }
      inTable = false;
      tableRows = [];
    }
  }

  function closeBlockquote() {
    if (inBlockquote) {
      const bqText = blockquoteLines.map(l => parseInline(l)).join('<br>');
      out.push(`<blockquote class="prose-quote">${bqText}</blockquote>`);
      inBlockquote = false;
      blockquoteLines = [];
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    const codeMatch = trimmed.match(/^%%CODE_BLOCK_(\d+)%%$/);
    if (codeMatch) {
      closeAllLists();
      closeTable();
      closeBlockquote();
      const idx = parseInt(codeMatch[1], 10);
      const { lang, code } = codeBlocks[idx];
      if (lang === 'mermaid') {
        out.push(`<div class="mermaid-diagram"><pre class="mermaid">${escapeHtml(code)}</pre></div>`);
      } else {
        out.push(`
<div class="code-block-card">
  <div class="code-block-header">
    <span class="code-lang-label">${lang || 'text'}</span>
    <button class="copy-code-btn" onclick="copySnippet(this)" title="Copy code">
      <span class="copy-btn-icon">📋</span> <span class="copy-btn-text">Copy</span>
    </button>
  </div>
  <pre class="code-pre"><code class="language-${lang || 'plaintext'}">${escapeHtml(code)}</code></pre>
</div>`);
      }
      continue;
    }

    const calloutMatch = trimmed.match(/^%%CALLOUT_(\d+)%%$/);
    if (calloutMatch) {
      closeAllLists();
      closeTable();
      closeBlockquote();
      const idx = parseInt(calloutMatch[1], 10);
      const { type, content } = callouts[idx];
      const parsedInner = content.split(/\r?\n/).map(l => parseInline(l)).join('<br>');
      const icons = {
        NOTE: 'ℹ️',
        TIP: '💡',
        IMPORTANT: '❗',
        WARNING: '⚠️',
        CAUTION: '🛑'
      };
      out.push(`
<div class="alert-callout callout-${type.toLowerCase()}">
  <div class="callout-header">
    <span class="callout-icon">${icons[type] || 'ℹ️'}</span>
    <span class="callout-title">${type}</span>
  </div>
  <div class="callout-content">
    ${parsedInner}
  </div>
</div>`);
      continue;
    }

    if (/^(\*{3,}|-{3,}|_{3,})$/.test(trimmed)) {
      closeAllLists();
      closeTable();
      closeBlockquote();
      out.push('<hr class="prose-hr">');
      continue;
    }

    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      closeAllLists();
      closeBlockquote();
      const cells = trimmed.slice(1, -1).split('|');
      const isDelimiter = cells.every(c => /^[\s:-]+$/.test(c.trim()));
      if (isDelimiter) {
        continue;
      }
      if (!inTable) {
        inTable = true;
        tableRows = [cells];
      } else {
        tableRows.push(cells);
      }
      continue;
    } else {
      closeTable();
    }

    if (trimmed.startsWith('>')) {
      closeAllLists();
      closeTable();
      if (!inBlockquote) {
        inBlockquote = true;
      }
      blockquoteLines.push(trimmed.replace(/^>[ \t]?/, ''));
      continue;
    } else {
      closeBlockquote();
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      closeAllLists();
      closeTable();
      closeBlockquote();
      let level = headingMatch[1].length;
      const headingText = headingMatch[2].trim();
      const slug = slugify(headingText.replace(/<[^>]+>/g, '').replace(/[^\w\s-]/g, '')) || `section-${i}`;

      if (isSubDocument && level === 1) {
        level = 2;
      }

      if (level >= 2 && level <= 4) {
        toc.push({ level, id: slug, text: headingText });
      }

      const parsedHeading = parseInline(headingText);
      out.push(`<h${level} id="${slug}" class="prose-h${level}">${parsedHeading} <a href="#${slug}" class="anchor-link" aria-label="Link to ${headingText}">#</a></h${level}>`);
      continue;
    }

    const olMatch = line.match(/^([ \t]*)(\d+)\.\s+(.*)$/);
    const ulMatch = line.match(/^([ \t]*)[*\-+]\s+(.*)$/);
    if (olMatch || ulMatch) {
      closeTable();
      closeBlockquote();
      const isOl = !!olMatch;
      const indentStr = isOl ? olMatch[1] : ulMatch[1];
      const indent = indentStr.replace(/\t/g, '  ').length;
      const itemText = isOl ? olMatch[3] : ulMatch[2];
      const listType = isOl ? 'ol' : 'ul';

      handleListItem(indent, listType, itemText);
      continue;
    }

    if (!trimmed) {
      continue;
    }

    closeAllLists();
    out.push(`<p class="prose-p">${parseInline(trimmed)}</p>`);
  }

  closeAllLists();
  closeTable();
  closeBlockquote();

  return { html: out.join('\n'), toc };
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

function renderHeader(activePage = 'Skills') {
  return `
    <header>
      <nav class="nav-bar">
        <a href="${BLOG_URL}" class="brand-link">
          danicat.dev
        </a>
        <div class="nav-links">
          <a href="${BLOG_URL}/posts/" class="nav-link">Posts</a>
          <a href="${BLOG_URL}/events/" class="nav-link">Events</a>
          <a href="${BLOG_URL}/codelabs/" class="nav-link">Codelabs</a>
          <a href="/" class="nav-link ${activePage === 'Skills' ? 'active' : ''}">Skills</a>
          <a href="${BLOG_URL}/about/" class="nav-link">About</a>
          <a href="${REPO_URL}" target="_blank" rel="noopener" class="nav-icon-link" aria-label="GitHub" title="GitHub">
            ${GITHUB_SVG}
          </a>
          <button id="themeToggle" class="nav-icon-btn" aria-label="Toggle light/dark theme" title="Toggle theme">
            <span class="dark-hidden">${MOON_SVG}</span>
            <span class="dark-visible">${SUN_SVG}</span>
          </button>
        </div>
      </nav>
    </header>`;
}

function renderFooter() {
  return `
    <footer>
      <p>© Daniela Petruzalek · Open source under Apache-2.0</p>
      <p><a href="${BLOG_URL}">← Back to danicat.dev</a> · <a href="${REPO_URL}">GitHub Repository</a> · <a href="/llms.txt">llms.txt</a> · <a href="/sitemap.xml">sitemap.xml</a></p>
    </footer>`;
}

const COMMON_CSS = `
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

      /* Callout Light */
      --callout-note-bg: #f0f9ff;
      --callout-note-border: #0284c7;
      --callout-tip-bg: #f0fdf4;
      --callout-tip-border: #16a34a;
      --callout-important-bg: #faf5ff;
      --callout-important-border: #9333ea;
      --callout-warning-bg: #fffbeb;
      --callout-warning-border: #d97706;
      --callout-caution-bg: #fef2f2;
      --callout-caution-border: #dc2626;
    }

    html.dark, html[data-theme="dark"] {
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

      /* Callout Dark */
      --callout-note-bg: rgba(2, 132, 199, 0.1);
      --callout-note-border: #38bdf8;
      --callout-tip-bg: rgba(22, 163, 74, 0.1);
      --callout-tip-border: #4ade80;
      --callout-important-bg: rgba(147, 51, 234, 0.1);
      --callout-important-border: #c084fc;
      --callout-warning-bg: rgba(217, 119, 6, 0.1);
      --callout-warning-border: #fbbf24;
      --callout-caution-bg: rgba(220, 38, 38, 0.1);
      --callout-caution-border: #f87171;
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

    /* Header */
    header {
      padding: 1.5rem 0 2rem;
      border-bottom: 1px solid var(--border);
      margin-bottom: 2rem;
    }

    .nav-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1.25rem;
    }

    .brand-link {
      display: inline-flex;
      align-items: center;
      text-decoration: none;
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-heading);
      letter-spacing: -0.01em;
      transition: color 0.15s ease;
    }

    .brand-link:hover { color: var(--primary); }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      flex-wrap: wrap;
    }

    .nav-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.95rem;
      font-weight: 500;
      transition: color 0.15s ease;
      display: inline-flex;
      align-items: center;
    }

    .nav-link:hover { color: var(--primary); }
    .nav-link.active { color: var(--text-heading); font-weight: 600; }

    .nav-icon-link, .nav-icon-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      padding: 0;
      line-height: 1;
      transition: color 0.15s ease;
      font-family: inherit;
    }

    .nav-icon-link:hover, .nav-icon-btn:hover { color: var(--primary); }
    .nav-icon-link svg, .nav-icon-btn svg { width: 1.15rem; height: 1.15rem; fill: currentColor; display: block; }

    .dark-hidden { display: inline-flex; align-items: center; justify-content: center; }
    .dark-visible { display: none; align-items: center; justify-content: center; }
    html.dark .dark-hidden, html[data-theme="dark"] .dark-hidden { display: none !important; }
    html.dark .dark-visible, html[data-theme="dark"] .dark-visible { display: inline-flex !important; }

    /* Breadcrumbs */
    .breadcrumbs {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
      font-size: 0.88rem;
      color: var(--text-muted);
      margin-bottom: 1.5rem;
    }

    .breadcrumbs a {
      color: var(--text-muted);
      text-decoration: none;
      transition: color 0.15s ease;
    }

    .breadcrumbs a:hover { color: var(--primary); }
    .breadcrumbs .sep { opacity: 0.5; }
    .breadcrumbs .current { color: var(--text-heading); font-weight: 600; }

    /* Detail Hero */
    .detail-hero {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2.5rem;
      box-shadow: var(--shadow);
    }

    .detail-hero-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }

    .detail-title-wrap h1 {
      font-size: 2.25rem;
      font-weight: 800;
      color: var(--text-heading);
      letter-spacing: -0.025em;
      line-height: 1.2;
    }

    .detail-desc {
      font-size: 1.1rem;
      color: var(--text);
      line-height: 1.6;
      margin-bottom: 1.5rem;
      max-width: 900px;
    }

    .meta-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
    }

    .meta-pill {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.82rem;
      font-weight: 500;
      padding: 0.25rem 0.65rem;
      border-radius: 9999px;
      background: var(--badge-bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
    }

    .meta-pill strong { color: var(--text-heading); }
    .meta-pill code {
      background: var(--code-bg);
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
      font-size: 0.78rem;
      font-family: var(--font-mono);
      color: var(--primary);
    }

    .install-widget {
      margin-bottom: 1.25rem;
    }

    .install-tabs {
      display: flex;
      gap: 0.35rem;
      margin-bottom: -1px;
      position: relative;
      z-index: 1;
      flex-wrap: wrap;
    }

    .install-tab-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      border-bottom: none;
      border-radius: 6px 6px 0 0;
      padding: 0.35rem 0.75rem;
      font-size: 0.8rem;
      font-weight: 600;
      font-family: var(--font-mono);
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .install-tab-btn:hover {
      color: var(--text-heading);
      background: var(--code-bg);
    }

    .install-tab-btn.active {
      color: var(--primary);
      background: var(--code-bg);
      border-color: var(--code-border);
      border-bottom: 1px solid var(--code-bg);
    }

    .install-tab-content {
      display: none;
    }

    .install-tab-content.active {
      display: block;
    }

    .install-tab-content .install-box {
      border-top-left-radius: 0;
      margin-bottom: 0;
    }

    .install-box {
      display: flex;
      align-items: center;
      background: var(--code-bg);
      border: 1px solid var(--code-border);
      border-radius: 8px;
      padding: 0.65rem 1rem;
      font-family: var(--font-mono);
      font-size: 0.92rem;
      color: var(--text-heading);
      margin-bottom: 1.25rem;
    }

    .install-cmd {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      padding-right: 0.75rem;
    }

    .copy-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-heading);
      cursor: pointer;
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.15s ease;
    }

    .copy-btn:hover {
      border-color: var(--primary);
      color: var(--primary);
    }

    .action-links {
      display: flex;
      flex-wrap: wrap;
      gap: 1.25rem;
      font-size: 0.9rem;
      font-weight: 500;
    }

    .action-links a {
      color: var(--primary);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: color 0.15s ease;
    }

    .action-links a:hover {
      color: var(--primary-hover);
      text-decoration: underline;
    }

    /* Content Layout (Main + Sidebar) */
    .content-layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 280px;
      gap: 3rem;
      align-items: start;
    }

    @media (max-width: 960px) {
      .content-layout {
        grid-template-columns: 1fr;
        gap: 2rem;
      }
      .sidebar {
        order: 2;
      }
    }

    /* Prose Styling */
    .prose {
      font-size: 1.05rem;
      line-height: 1.75;
      color: var(--text);
    }

    .prose-h1, .prose-h2, .prose-h3, .prose-h4 {
      color: var(--text-heading);
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-top: 2.25rem;
      margin-bottom: 1rem;
      position: relative;
    }

    .prose-h1 { font-size: 1.85rem; }
    .prose-h2 {
      font-size: 1.45rem;
      padding-bottom: 0.4rem;
      border-bottom: 1px solid var(--border);
    }
    .prose-h3 { font-size: 1.2rem; }
    .prose-h4 { font-size: 1.05rem; }

    .anchor-link {
      opacity: 0;
      text-decoration: none;
      color: var(--text-muted);
      margin-left: 0.35rem;
      font-weight: 400;
      transition: opacity 0.15s ease;
    }

    .prose-h1:hover .anchor-link,
    .prose-h2:hover .anchor-link,
    .prose-h3:hover .anchor-link,
    .prose-h4:hover .anchor-link {
      opacity: 0.75;
    }

    .anchor-link:hover { opacity: 1 !important; color: var(--primary); }

    .prose-p {
      margin-bottom: 1.25rem;
    }

    .prose-ul, .prose-ol {
      margin-bottom: 1.25rem;
      padding-left: 1.5rem;
    }

    .prose-ul li, .prose-ol li {
      margin-bottom: 0.45rem;
    }

    .task-list-item {
      list-style-type: none;
      margin-left: -1.25rem;
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
    }

    .task-check {
      accent-color: var(--primary);
    }

    .inline-code {
      font-family: var(--font-mono);
      font-size: 0.88em;
      background: var(--badge-bg);
      border: 1px solid var(--border);
      padding: 0.15em 0.35em;
      border-radius: 4px;
      color: var(--text-heading);
    }

    .math-inline, .math-display {
      font-family: var(--font-mono);
      font-size: 0.92em;
      color: var(--primary);
      background: var(--primary-subtle);
      padding: 0.15em 0.35em;
      border-radius: 4px;
    }

    .prose-quote {
      border-left: 4px solid var(--primary);
      padding: 0.6rem 1.25rem;
      margin: 1.5rem 0;
      background: var(--primary-subtle);
      border-radius: 0 8px 8px 0;
      color: var(--text);
    }

    .prose-hr {
      border: none;
      border-top: 1px solid var(--border);
      margin: 2.5rem 0;
    }

    .prose a {
      color: var(--primary);
      text-decoration: none;
      transition: color 0.15s ease;
    }

    .prose a:hover {
      text-decoration: underline;
      color: var(--primary-hover);
    }

    .ext-icon { font-size: 0.8em; }

    /* Code Blocks */
    .code-block-card {
      background: var(--code-bg);
      border: 1px solid var(--code-border);
      border-radius: 10px;
      margin: 1.5rem 0;
      overflow: hidden;
      box-shadow: var(--shadow);
    }

    .code-block-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.45rem 0.85rem;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      font-size: 0.78rem;
    }

    .code-lang-label {
      font-family: var(--font-mono);
      font-weight: 600;
      text-transform: uppercase;
      color: var(--text-muted);
      letter-spacing: 0.04em;
    }

    .copy-code-btn {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-muted);
      cursor: pointer;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.78rem;
      display: flex;
      align-items: center;
      gap: 0.3rem;
      transition: all 0.15s ease;
    }

    .copy-code-btn:hover {
      color: var(--text-heading);
      border-color: var(--primary);
    }

    .code-pre {
      padding: 1rem 1.25rem;
      overflow-x: auto;
      font-family: var(--font-mono);
      font-size: 0.88rem;
      line-height: 1.6;
      color: var(--text-heading);
    }

    /* Mermaid Diagrams */
    .mermaid-diagram {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.5rem;
      margin: 1.75rem 0;
      display: flex;
      justify-content: center;
      overflow-x: auto;
    }

    /* Tables */
    .table-wrap {
      overflow-x: auto;
      margin: 1.75rem 0;
      border: 1px solid var(--border);
      border-radius: 8px;
    }

    .prose-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.95rem;
    }

    .prose-table th, .prose-table td {
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--border);
    }

    .prose-table th {
      background: var(--badge-bg);
      color: var(--text-heading);
      font-weight: 600;
    }

    .prose-table tr:last-child td { border-bottom: none; }
    .prose-table tr:hover td { background: var(--surface-hover); }

    /* Callouts */
    .alert-callout {
      border-radius: 8px;
      padding: 1.25rem;
      margin: 1.5rem 0;
      border-left: 4px solid;
    }

    .callout-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 700;
      font-size: 0.95rem;
      margin-bottom: 0.65rem;
      color: var(--text-heading);
    }

    .callout-note { background: var(--callout-note-bg); border-color: var(--callout-note-border); }
    .callout-tip { background: var(--callout-tip-bg); border-color: var(--callout-tip-border); }
    .callout-important { background: var(--callout-important-bg); border-color: var(--callout-important-border); }
    .callout-warning { background: var(--callout-warning-bg); border-color: var(--callout-warning-border); }
    .callout-caution { background: var(--callout-caution-bg); border-color: var(--callout-caution-border); }

    /* Sidebar Widgets */
    .sidebar {
      position: sticky;
      top: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.75rem;
    }

    .sidebar-widget {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.25rem;
      box-shadow: var(--shadow);
    }

    .widget-title {
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 0.85rem;
    }

    .toc-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      font-size: 0.88rem;
    }

    .toc-item a {
      color: var(--text-muted);
      text-decoration: none;
      transition: color 0.15s ease;
      display: block;
      line-height: 1.4;
    }

    .toc-item a:hover { color: var(--primary); }
    .toc-item.level-3 { padding-left: 0.85rem; font-size: 0.84rem; }
    .toc-item.level-4 { padding-left: 1.5rem; font-size: 0.8rem; }

    .resource-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      font-size: 0.86rem;
    }

    .resource-item a {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--text);
      text-decoration: none;
      transition: color 0.15s ease;
      word-break: break-all;
    }

    .resource-item a:hover { color: var(--primary); }

    .related-skills-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      font-size: 0.88rem;
    }

    .related-skills-list a {
      color: var(--text);
      text-decoration: none;
      display: block;
      transition: color 0.15s ease;
    }

    .related-skills-list a:hover { color: var(--primary); }
`;

function generateSkillHtml(skill, allSkillsInCategory, bundledResources) {
  const { html: bodyHtml, toc } = markdownToHtml(skill.body, { isSubDocument: true });
  const title = `${skill.name} · Agent Skill · danicat.dev`;
  const canonicalUrl = `${DOMAIN}/${skill.category}/${skill.folder}/`;

  const metaAuthor = skill.metadata?.author || 'Daniela Petruzalek (daniela@danicat.dev)';
  const metaVersion = skill.metadata?.version || '';
  const todayIso = new Date().toISOString().split('T')[0];

  const catObj = CATEGORIES.find(c => c.id === skill.category);
  const categoryName = catObj ? catObj.name : skill.categoryName || skill.category;

  const schemaGraph = {
    '@context': 'https://schema.org',
    '@graph': [
      SCHEMA_AUTHOR,
      SCHEMA_PUBLISHER,
      {
        '@type': 'SoftwareApplication',
        '@id': `${canonicalUrl}#software`,
        name: skill.name,
        applicationCategory: 'DeveloperApplication',
        operatingSystem: 'Any',
        offers: {
          '@type': 'Offer',
          price: '0',
          priceCurrency: 'USD'
        },
        description: skill.description,
        softwareVersion: skill.version || '0.1.0',
        license: 'https://www.apache.org/licenses/LICENSE-2.0',
        url: canonicalUrl,
        downloadUrl: skill.url,
        codeRepository: skill.githubUrl,
        author: { '@id': 'https://danicat.dev/#person' },
        publisher: { '@id': `${DOMAIN}/#organization` }
      },
      {
        '@type': 'TechArticle',
        '@id': `${canonicalUrl}#article`,
        headline: `${skill.name} Agent Skill`,
        description: skill.description,
        url: canonicalUrl,
        mainEntityOfPage: canonicalUrl,
        datePublished: '2025-01-01',
        dateModified: todayIso,
        author: { '@id': 'https://danicat.dev/#person' },
        publisher: { '@id': `${DOMAIN}/#organization` },
        about: { '@id': `${canonicalUrl}#software` }
      },
      {
        '@type': 'BreadcrumbList',
        '@id': `${canonicalUrl}#breadcrumbs`,
        itemListElement: [
          {
            '@type': 'ListItem',
            position: 1,
            name: 'Catalog',
            item: `${DOMAIN}/`
          },
          {
            '@type': 'ListItem',
            position: 2,
            name: categoryName,
            item: `${DOMAIN}/${skill.category}/`
          },
          {
            '@type': 'ListItem',
            position: 3,
            name: skill.name,
            item: canonicalUrl
          }
        ]
      }
    ]
  };

  return `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(skill.description)}">
  <link rel="canonical" href="${canonicalUrl}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="theme-color" content="#0f172a">
  <meta name="color-scheme" content="dark light">

  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '${GA_MEASUREMENT_ID}');
  </script>

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="${canonicalUrl}">
  <meta property="og:title" content="${escapeHtml(skill.name)} · Agent Skill">
  <meta property="og:description" content="${escapeHtml(skill.description)}">
  <meta property="og:site_name" content="Daniela Petruzalek (danicat.dev)">
  <meta property="og:image" content="${BLOG_URL}/apple-touch-icon.png">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="${escapeHtml(skill.name)} · Agent Skill">
  <meta name="twitter:description" content="${escapeHtml(skill.description)}">
  <meta name="twitter:image" content="${BLOG_URL}/apple-touch-icon.png">
  <meta name="twitter:creator" content="@danicat83">

  <!-- JSON-LD Schema -->
  <script type="application/ld+json">
${JSON.stringify(schemaGraph, null, 2)}
  </script>

  <link rel="icon" type="image/png" sizes="32x32" href="${BLOG_URL}/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="${BLOG_URL}/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="${BLOG_URL}/apple-touch-icon.png">

  <script>
    (function() {
      var appearance = localStorage.getItem('appearance');
      if (appearance === 'dark' || (!appearance && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.setAttribute('data-theme', 'light');
      }
    })();
  </script>

  <style>
${COMMON_CSS}
  </style>

  <!-- Mermaid.js for architecture diagrams -->
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    const isDark = document.documentElement.classList.contains('dark') || document.documentElement.getAttribute('data-theme') === 'dark';
    mermaid.initialize({
      startOnLoad: true,
      theme: isDark ? 'dark' : 'default',
      securityLevel: 'loose'
    });
  </script>
</head>
<body>
  <div class="container">
    ${renderHeader('Skills')}

    <nav class="breadcrumbs" aria-label="Breadcrumbs">
      <a href="/">Catalog</a>
      <span class="sep">/</span>
      <a href="/${skill.category}/">${skill.categoryEmoji} ${escapeHtml(skill.categoryName)}</a>
      <span class="sep">/</span>
      <span class="current">${escapeHtml(skill.name)}</span>
    </nav>

    <div class="detail-hero">
      <div class="detail-hero-header">
        <div class="detail-title-wrap">
          <h1>${escapeHtml(skill.name)}</h1>
        </div>
        <span class="meta-pill">${skill.categoryEmoji} ${escapeHtml(skill.categoryName)}</span>
      </div>

      <p class="detail-desc">${escapeHtml(skill.description)}</p>

      <div class="meta-pills">
        <span class="meta-pill"><strong>Version:</strong> v${escapeHtml(skill.version || '0.1.0')}</span>
        <span class="meta-pill"><strong>License:</strong> ${escapeHtml(skill.license)}</span>
        <span class="meta-pill"><strong>Author:</strong> ${escapeHtml(skill.author || 'Daniela Petruzalek')}</span>
        <span class="meta-pill" title="${escapeHtml(skill.digest || '')}"><strong>Digest:</strong> <code>${escapeHtml((skill.sha256 || '').slice(0, 8))}</code></span>
      </div>

      <div class="install-widget">
        <div class="install-tabs">
          <button type="button" class="install-tab-btn active" onclick="switchInstallTab(this, 'tab-npx-add')">npx skills add</button>${ENABLE_KUNGFU ? `
          <button type="button" class="install-tab-btn kungfu-tab" onclick="switchInstallTab(this, 'tab-kungfu-load')">kungfu load (JIT)</button>
          <button type="button" class="install-tab-btn kungfu-tab" onclick="switchInstallTab(this, 'tab-kungfu-learn')">kungfu learn (Persist)</button>` : ''}
          <button type="button" class="install-tab-btn" onclick="switchInstallTab(this, 'tab-raw-url')">Raw URL</button>
        </div>

        <div id="tab-npx-add" class="install-tab-content active">
          <div class="install-box">
            <span class="install-cmd">${escapeHtml(skill.installCommand)}</span>
            <button type="button" class="copy-btn" onclick="copyInstallCommand('${escapeHtml(skill.installCommand)}', this)" title="Copy command">
              <span>📋</span> Copy
            </button>
          </div>
        </div>${ENABLE_KUNGFU ? `

        <div id="tab-kungfu-load" class="install-tab-content kungfu-pane">
          <div class="install-box">
            <span class="install-cmd">${escapeHtml(skill.kungfuLoadCommand)}</span>
            <button type="button" class="copy-btn" onclick="copyInstallCommand('${escapeHtml(skill.kungfuLoadCommand)}', this)" title="Copy command">
              <span>📋</span> Copy
            </button>
          </div>
        </div>

        <div id="tab-kungfu-learn" class="install-tab-content kungfu-pane">
          <div class="install-box">
            <span class="install-cmd">${escapeHtml(skill.kungfuLearnCommand)}</span>
            <button type="button" class="copy-btn" onclick="copyInstallCommand('${escapeHtml(skill.kungfuLearnCommand)}', this)" title="Copy command">
              <span>📋</span> Copy
            </button>
          </div>
        </div>` : ''}

        <div id="tab-raw-url" class="install-tab-content">
          <div class="install-box">
            <span class="install-cmd">${escapeHtml(skill.url)}</span>
            <button type="button" class="copy-btn" onclick="copyInstallCommand('${escapeHtml(skill.url)}', this)" title="Copy URL">
              <span>📋</span> Copy
            </button>
          </div>
        </div>
      </div>

      <div class="action-links">
        <a href="./SKILL.md">📄 Raw SKILL.md</a>
        <a href="${skill.githubUrl}" target="_blank" rel="noopener">🐙 GitHub Source</a>
        <a href="/">← Back to Catalog</a>
      </div>
    </div>

    <div class="content-layout">
      <main class="prose">
        ${bodyHtml}
      </main>

      <aside class="sidebar">
        ${toc.length > 0 ? `
        <div class="sidebar-widget">
          <div class="widget-title">On This Page</div>
          <ul class="toc-list">
            ${toc.map(t => `<li class="toc-item level-${t.level}"><a href="#${t.id}">${escapeHtml(t.text)}</a></li>`).join('\n            ')}
          </ul>
        </div>` : ''}

        ${bundledResources.length > 0 ? `
        <div class="sidebar-widget">
          <div class="widget-title">Bundled Files</div>
          <ul class="resource-list">
            ${bundledResources.map(r => {
              const icon = r.isMarkdown ? '📄' : (r.name.endsWith('.py') ? '🐍' : (r.name.endsWith('.sh') ? '📜' : (r.name.endsWith('.json') ? '📋' : '📁')));
              const targetUrl = r.isMarkdown ? r.relPath.replace(/\.md$/, '.html') : r.relPath;
              return `<li class="resource-item"><a href="./${targetUrl}"><span>${icon}</span> ${escapeHtml(r.relPath)}</a></li>`;
            }).join('\n            ')}
          </ul>
        </div>` : ''}

        <div class="sidebar-widget">
          <div class="widget-title">More in ${escapeHtml(skill.categoryName)}</div>
          <ul class="related-skills-list">
            ${allSkillsInCategory.filter(s => s.name !== skill.name).map(s => `
              <li><a href="/${s.category}/${s.folder}/">${s.name} →</a></li>
            `).join('\n            ')}
          </ul>
        </div>
      </aside>
    </div>

    ${renderFooter()}
  </div>

  <script>
    // Theme Management
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;

    function applyTheme(theme) {
      if (theme === 'dark') {
        htmlEl.classList.add('dark');
        htmlEl.setAttribute('data-theme', 'dark');
      } else {
        htmlEl.classList.remove('dark');
        htmlEl.setAttribute('data-theme', 'light');
      }
      localStorage.setItem('appearance', theme);
    }

    const savedTheme = localStorage.getItem('appearance') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(savedTheme);

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = htmlEl.classList.contains('dark') || htmlEl.getAttribute('data-theme') === 'dark';
        applyTheme(isDark ? 'light' : 'dark');
      });
    }

    function switchInstallTab(btn, targetId) {
      const widget = btn.closest('.install-widget');
      if (!widget) return;
      widget.querySelectorAll('.install-tab-btn').forEach(b => b.classList.remove('active'));
      widget.querySelectorAll('.install-tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = widget.querySelector('#' + targetId);
      if (target) target.classList.add('active');
    }

    function copyInstallCommand(cmd, btn) {
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

    function copySnippet(btn) {
      const pre = btn.closest('.code-block-card').querySelector('code');
      if (!pre) return;
      navigator.clipboard.writeText(pre.innerText).then(() => {
        const textEl = btn.querySelector('.copy-btn-text');
        const iconEl = btn.querySelector('.copy-btn-icon');
        const origText = textEl.innerText;
        textEl.innerText = 'Copied!';
        iconEl.innerText = '✓';
        btn.style.borderColor = 'var(--green)';
        btn.style.color = 'var(--green)';
        setTimeout(() => {
          textEl.innerText = origText;
          iconEl.innerText = '📋';
          btn.style.borderColor = '';
          btn.style.color = '';
        }, 1500);
      });
    }
  </script>
</body>
</html>`;
}

function generateReferenceHtml(refFile, skill, content) {
  const { data, body } = parseFrontmatter(content);
  const { html: bodyHtml, toc } = markdownToHtml(body, { isSubDocument: true });
  const refTitle = data.title || refFile.name.replace(/\.md$/, '').replace(/[_-]/g, ' ');
  const title = `${refTitle} · ${skill.name} · danicat.dev`;
  const canonicalUrl = `${DOMAIN}/${skill.category}/${skill.folder}/${refFile.relPath.replace(/\.md$/, '.html')}`;
  const skillDetailUrl = `${DOMAIN}/${skill.category}/${skill.folder}/`;
  const refDescription = data.description || `${refTitle} reference guide and architectural documentation for ${skill.name}.`;
  const todayIso = new Date().toISOString().split('T')[0];

  const catObj = CATEGORIES.find(c => c.id === skill.category);
  const categoryName = catObj ? catObj.name : skill.categoryName || skill.category;

  const schemaGraph = {
    '@context': 'https://schema.org',
    '@graph': [
      SCHEMA_AUTHOR,
      SCHEMA_PUBLISHER,
      {
        '@type': 'TechArticle',
        '@id': `${canonicalUrl}#article`,
        headline: `${refTitle} · ${skill.name} Reference`,
        description: refDescription,
        url: canonicalUrl,
        mainEntityOfPage: canonicalUrl,
        datePublished: '2025-01-01',
        dateModified: todayIso,
        author: { '@id': 'https://danicat.dev/#person' },
        publisher: { '@id': `${DOMAIN}/#organization` },
        isPartOf: {
          '@type': 'SoftwareApplication',
          name: skill.name,
          url: skillDetailUrl
        }
      },
      {
        '@type': 'BreadcrumbList',
        '@id': `${canonicalUrl}#breadcrumbs`,
        itemListElement: [
          {
            '@type': 'ListItem',
            position: 1,
            name: 'Catalog',
            item: `${DOMAIN}/`
          },
          {
            '@type': 'ListItem',
            position: 2,
            name: categoryName,
            item: `${DOMAIN}/${skill.category}/`
          },
          {
            '@type': 'ListItem',
            position: 3,
            name: skill.name,
            item: skillDetailUrl
          },
          {
            '@type': 'ListItem',
            position: 4,
            name: refTitle,
            item: canonicalUrl
          }
        ]
      }
    ]
  };

  return `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(refDescription)}">
  <link rel="canonical" href="${canonicalUrl}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="theme-color" content="#0f172a">
  <meta name="color-scheme" content="dark light">

  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '${GA_MEASUREMENT_ID}');
  </script>

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="${canonicalUrl}">
  <meta property="og:title" content="${escapeHtml(refTitle)} · ${escapeHtml(skill.name)} Reference">
  <meta property="og:description" content="${escapeHtml(refDescription)}">
  <meta property="og:site_name" content="Daniela Petruzalek (danicat.dev)">
  <meta property="og:image" content="${BLOG_URL}/apple-touch-icon.png">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="${escapeHtml(refTitle)} · ${escapeHtml(skill.name)} Reference">
  <meta name="twitter:description" content="${escapeHtml(refDescription)}">
  <meta name="twitter:image" content="${BLOG_URL}/apple-touch-icon.png">
  <meta name="twitter:creator" content="@danicat83">

  <!-- JSON-LD Schema -->
  <script type="application/ld+json">
${JSON.stringify(schemaGraph, null, 2)}
  </script>

  <link rel="icon" type="image/png" sizes="32x32" href="${BLOG_URL}/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="${BLOG_URL}/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="${BLOG_URL}/apple-touch-icon.png">

  <script>
    (function() {
      var appearance = localStorage.getItem('appearance');
      if (appearance === 'dark' || (!appearance && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.setAttribute('data-theme', 'light');
      }
    })();
  </script>

  <style>
${COMMON_CSS}
  </style>

  <!-- Mermaid.js for diagrams -->
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    const isDark = document.documentElement.classList.contains('dark') || document.documentElement.getAttribute('data-theme') === 'dark';
    mermaid.initialize({
      startOnLoad: true,
      theme: isDark ? 'dark' : 'default',
      securityLevel: 'loose'
    });
  </script>
</head>
<body>
  <div class="container">
    ${renderHeader('Skills')}

    <nav class="breadcrumbs" aria-label="Breadcrumbs">
      <a href="/">Catalog</a>
      <span class="sep">/</span>
      <a href="/${skill.category}/">${skill.categoryEmoji} ${escapeHtml(skill.categoryName)}</a>
      <span class="sep">/</span>
      <a href="/${skill.category}/${skill.folder}/">${escapeHtml(skill.name)}</a>
      <span class="sep">/</span>
      <span class="current">${escapeHtml(refFile.relPath)}</span>
    </nav>

    <div class="detail-hero">
      <div class="detail-hero-header">
        <div class="detail-title-wrap">
          <h1>${escapeHtml(refTitle)}</h1>
        </div>
        <span class="meta-pill">${skill.categoryEmoji} ${escapeHtml(skill.name)}</span>
      </div>

      <div class="action-links">
        <a href="/${skill.category}/${skill.folder}/">← Back to ${escapeHtml(skill.name)}</a>
        <a href="./${refFile.name}">📄 Raw Markdown</a>
      </div>
    </div>

    <div class="content-layout">
      <main class="prose">
        ${bodyHtml}
      </main>

      <aside class="sidebar">
        ${toc.length > 0 ? `
        <div class="sidebar-widget">
          <div class="widget-title">On This Page</div>
          <ul class="toc-list">
            ${toc.map(t => `<li class="toc-item level-${t.level}"><a href="#${t.id}">${escapeHtml(t.text)}</a></li>`).join('\n            ')}
          </ul>
        </div>` : ''}

        <div class="sidebar-widget">
          <div class="widget-title">Parent Skill</div>
          <p style="font-size: 0.9rem; margin-bottom: 0.75rem;">${escapeHtml(skill.description)}</p>
          <a href="/${skill.category}/${skill.folder}/" style="color: var(--primary); font-size: 0.88rem; font-weight: 500;">View ${escapeHtml(skill.name)} →</a>
        </div>
      </aside>
    </div>

    ${renderFooter()}
  </div>

  <script>
    // Theme Management
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;

    function applyTheme(theme) {
      if (theme === 'dark') {
        htmlEl.classList.add('dark');
        htmlEl.setAttribute('data-theme', 'dark');
      } else {
        htmlEl.classList.remove('dark');
        htmlEl.setAttribute('data-theme', 'light');
      }
      localStorage.setItem('appearance', theme);
    }

    const savedTheme = localStorage.getItem('appearance') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(savedTheme);

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = htmlEl.classList.contains('dark') || htmlEl.getAttribute('data-theme') === 'dark';
        applyTheme(isDark ? 'light' : 'dark');
      });
    }

    function copySnippet(btn) {
      const pre = btn.closest('.code-block-card').querySelector('code');
      if (!pre) return;
      navigator.clipboard.writeText(pre.innerText).then(() => {
        const textEl = btn.querySelector('.copy-btn-text');
        const iconEl = btn.querySelector('.copy-btn-icon');
        const origText = textEl.innerText;
        textEl.innerText = 'Copied!';
        iconEl.innerText = '✓';
        btn.style.borderColor = 'var(--green)';
        btn.style.color = 'var(--green)';
        setTimeout(() => {
          textEl.innerText = origText;
          iconEl.innerText = '📋';
          btn.style.borderColor = '';
          btn.style.color = '';
        }, 1500);
      });
    }
  </script>
</body>
</html>`;
}

function generateCategoryHtml(category, skillsInCategory, allCategories, allSkills) {
  const title = `${category.name} Agent Skills · danicat.dev`;
  const canonicalUrl = `${DOMAIN}/${category.id}/`;

  const schemaGraph = {
    '@context': 'https://schema.org',
    '@graph': [
      SCHEMA_AUTHOR,
      SCHEMA_PUBLISHER,
      {
        '@type': 'CollectionPage',
        '@id': `${canonicalUrl}#page`,
        url: canonicalUrl,
        name: `${category.name} Agent Skills`,
        description: category.description,
        isPartOf: { '@id': `${DOMAIN}/#website` },
        about: {
          '@type': 'ItemList',
          name: `${category.name} Skills`,
          itemListElement: skillsInCategory.map((s, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            url: s.detailUrl,
            name: s.name,
            description: s.description
          }))
        }
      },
      {
        '@type': 'BreadcrumbList',
        '@id': `${canonicalUrl}#breadcrumbs`,
        itemListElement: [
          {
            '@type': 'ListItem',
            position: 1,
            name: 'Catalog',
            item: `${DOMAIN}/`
          },
          {
            '@type': 'ListItem',
            position: 2,
            name: category.name,
            item: canonicalUrl
          }
        ]
      }
    ]
  };

  return `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(category.description)}">
  <link rel="canonical" href="${canonicalUrl}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="theme-color" content="#0f172a">
  <meta name="color-scheme" content="dark light">

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
  <meta property="og:url" content="${canonicalUrl}">
  <meta property="og:title" content="${escapeHtml(category.emoji)} ${escapeHtml(category.name)} · Agent Skills">
  <meta property="og:description" content="${escapeHtml(category.description)}">
  <meta property="og:site_name" content="Daniela Petruzalek (danicat.dev)">
  <meta property="og:image" content="${BLOG_URL}/apple-touch-icon.png">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="${escapeHtml(category.emoji)} ${escapeHtml(category.name)} · Agent Skills">
  <meta name="twitter:description" content="${escapeHtml(category.description)}">
  <meta name="twitter:image" content="${BLOG_URL}/apple-touch-icon.png">
  <meta name="twitter:creator" content="@danicat83">

  <!-- JSON-LD Schema -->
  <script type="application/ld+json">
${JSON.stringify(schemaGraph, null, 2)}
  </script>

  <link rel="icon" type="image/png" sizes="32x32" href="${BLOG_URL}/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="${BLOG_URL}/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="${BLOG_URL}/apple-touch-icon.png">

  <script>
    (function() {
      var appearance = localStorage.getItem('appearance');
      if (appearance === 'dark' || (!appearance && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.setAttribute('data-theme', 'light');
      }
    })();
  </script>

  <style>
${COMMON_CSS}

    /* Category Hero */
    .cat-hero {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 2.25rem 2rem;
      margin-bottom: 2rem;
      box-shadow: var(--shadow);
    }

    .cat-hero-title-row {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 0.75rem;
    }

    .cat-hero-emoji {
      font-size: 2.5rem;
      line-height: 1;
    }

    .cat-hero-title-row h1 {
      font-size: 2.25rem;
      font-weight: 800;
      color: var(--text-heading);
      letter-spacing: -0.025em;
      line-height: 1.2;
    }

    .cat-hero-desc {
      font-size: 1.15rem;
      color: var(--text);
      line-height: 1.6;
      margin-bottom: 1.25rem;
      max-width: 800px;
    }

    /* Search & Filter Bar */
    .search-filter-section {
      margin-bottom: 2rem;
    }

    .search-input-wrapper {
      position: relative;
      margin-bottom: 1.25rem;
    }

    .search-input-wrapper input {
      width: 100%;
      padding: 0.85rem 1rem 0.85rem 2.75rem;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text-heading);
      font-size: 1rem;
      font-family: inherit;
      box-shadow: var(--shadow);
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
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
      font-size: 1.1rem;
      opacity: 0.6;
      pointer-events: none;
    }

    .category-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .pill-btn {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.45rem 0.95rem;
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 9999px;
      font-size: 0.88rem;
      font-weight: 500;
      cursor: pointer;
      text-decoration: none;
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
  </style>
</head>
<body>
  <div class="container">
    ${renderHeader('Skills')}

    <nav class="breadcrumbs" aria-label="Breadcrumbs">
      <a href="/">Catalog</a>
      <span class="sep">/</span>
      <span class="current">${category.emoji} ${escapeHtml(category.name)}</span>
    </nav>

    <div class="cat-hero">
      <div class="cat-hero-title-row">
        <span class="cat-hero-emoji">${category.emoji}</span>
        <h1>${escapeHtml(category.name)}</h1>
      </div>
      <p class="cat-hero-desc">${escapeHtml(category.description)}</p>
      <div class="meta-pills">
        <span class="meta-pill"><strong>Total Skills:</strong> ${skillsInCategory.length}</span>
        <span class="meta-pill"><strong>Format:</strong> Agent Skills (SKILL.md)</span>
        <span class="meta-pill"><strong>License:</strong> Apache-2.0</span>
      </div>
    </div>

    <section class="search-filter-section">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Filter ${escapeHtml(category.name)} skills by keyword... (Press '/' to focus)" autofocus>
      </div>
      <div class="category-pills">
        <a href="/" class="pill-btn">← All Skills (${allSkills.length})</a>
        ${allCategories.map(c => `
          <a href="/${c.id}/" class="pill-btn ${c.id === category.id ? 'active' : ''}">${c.emoji} ${escapeHtml(c.name)} (${allSkills.filter(s => s.category === c.id).length})</a>
        `).join('')}
      </div>${ENABLE_KUNGFU ? `
      <div class="cli-mode-bar" style="display: flex; align-items: center; gap: 0.6rem; font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
        <span style="font-weight: 500;">CLI Mode:</span>
        <div class="cli-mode-pills" style="display: flex; gap: 0.35rem;">
          <button type="button" class="mode-pill active" onclick="setGlobalCliMode('npx', this)">npx skills</button>
          <button type="button" class="mode-pill" onclick="setGlobalCliMode('kungfu-load', this)">kungfu load</button>
          <button type="button" class="mode-pill" onclick="setGlobalCliMode('kungfu-learn', this)">kungfu learn</button>
          <button type="button" class="mode-pill" onclick="setGlobalCliMode('raw-url', this)">Raw URL</button>
        </div>
      </div>` : ''}
    </section>

    <main>
      <div class="skills-grid" id="skillsGrid">
        ${skillsInCategory.map(s => `
        <div class="skill-card" data-category="${s.category}" data-name="${s.name.toLowerCase()}" data-desc="${s.description.toLowerCase().replace(/"/g, '&quot;')}">
          <div class="card-top">
            <div class="card-title-row">
              <a href="/${s.category}/${s.folder}/" class="skill-name-link">${s.name}</a>
              <span class="cat-badge">v${s.version}</span>
            </div>
            <p class="skill-description">${s.description}</p>
          </div>
          <div class="card-bottom">
            <div class="cmd-box" ${ENABLE_KUNGFU ? `data-npx="${escapeHtml(s.installCommand)}" data-kungfu-load="${escapeHtml(s.kungfuLoadCommand)}" data-kungfu-learn="${escapeHtml(s.kungfuLearnCommand)}" data-raw-url="${escapeHtml(s.url)}"` : ''}>
              <span class="cmd-text">${s.installCommand}</span>
              <button class="copy-button" onclick="copyInstall(this.previousElementSibling.innerText, this)" title="Copy install command">📋</button>
            </div>
            <div class="card-links">
              <a href="/${s.category}/${s.folder}/">View Skill →</a>
              <a href="/${s.relativePath}">Raw SKILL.md</a>
              <a href="${s.githubUrl}" target="_blank" rel="noopener">Source ↗</a>
            </div>
          </div>
        </div>`).join('')}
      </div>
    </main>

    ${renderFooter()}
  </div>

  <script>
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;

    function applyTheme(theme) {
      if (theme === 'dark') {
        htmlEl.classList.add('dark');
        htmlEl.setAttribute('data-theme', 'dark');
      } else {
        htmlEl.classList.remove('dark');
        htmlEl.setAttribute('data-theme', 'light');
      }
      localStorage.setItem('appearance', theme);
    }

    const savedTheme = localStorage.getItem('appearance') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(savedTheme);

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = htmlEl.classList.contains('dark') || htmlEl.getAttribute('data-theme') === 'dark';
        applyTheme(isDark ? 'light' : 'dark');
      });
    }

    const searchInput = document.getElementById('searchInput');
    const cards = document.querySelectorAll('.skill-card');
    const grid = document.getElementById('skillsGrid');

    function filterSkills() {
      const query = searchInput.value.toLowerCase().trim();
      let count = 0;

      cards.forEach(card => {
        const name = card.getAttribute('data-name');
        const desc = card.getAttribute('data-desc');
        const matchesQuery = !query || name.includes(query) || desc.includes(query);

        if (matchesQuery) {
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
    }${ENABLE_KUNGFU ? `

    function setGlobalCliMode(mode, btn) {
      document.querySelectorAll('.mode-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      localStorage.setItem('preferred_cli_mode', mode);
      document.querySelectorAll('.cmd-box').forEach(box => {
        const textSpan = box.querySelector('.cmd-text');
        if (!textSpan) return;
        if (mode === 'kungfu-load') {
          textSpan.innerText = box.getAttribute('data-kungfu-load');
        } else if (mode === 'kungfu-learn') {
          textSpan.innerText = box.getAttribute('data-kungfu-learn');
        } else if (mode === 'raw-url') {
          textSpan.innerText = box.getAttribute('data-raw-url');
        } else {
          textSpan.innerText = box.getAttribute('data-npx');
        }
      });
    }

    const savedMode = localStorage.getItem('preferred_cli_mode');
    if (savedMode) {
      const modeBtn = document.querySelector('.mode-pill[onclick*="' + savedMode + '"]');
      if (modeBtn) setGlobalCliMode(savedMode, modeBtn);
    }` : ''}
  </script>
</body>
</html>`;
}

async function build() {
  console.log('Building skills catalog with detail pages, sitemap.xml, robots.txt, and SEO...');

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
        url: `${DOMAIN}/${cat.id}/${skillFolder}/SKILL.md`,
        detailUrl: `${DOMAIN}/${cat.id}/${skillFolder}/`,
        githubUrl: `${REPO_URL}/tree/main/${cat.id}/${skillFolder}`,
        relativePath: `${cat.id}/${skillFolder}/SKILL.md`,
        body: body.trim(),
      };

      skills.push(skillRecord);
      copyRecursive(path.join(catDir, skillFolder), path.join(SITE_DIR, cat.id, skillFolder));
    }
  }

  const allReferencePages = [];

  // Generate Detail HTML pages for all skills
  for (const skill of skills) {
    const catSkills = skills.filter(s => s.category === skill.category);
    const skillDir = path.join(ROOT_DIR, skill.category, skill.folder);
    const resources = discoverBundledResources(skillDir);

    const detailHtml = generateSkillHtml(skill, catSkills, resources);
    fs.writeFileSync(path.join(SITE_DIR, skill.category, skill.folder, 'index.html'), detailHtml);

    // Generate HTML for bundled markdown reference files
    for (const res of resources) {
      if (res.isMarkdown) {
        const fullRefPath = path.join(skillDir, res.relPath);
        if (fs.existsSync(fullRefPath)) {
          const refContent = fs.readFileSync(fullRefPath, 'utf8');
          const refHtml = generateReferenceHtml(res, skill, refContent);
          const outRefHtmlPath = path.join(SITE_DIR, skill.category, skill.folder, res.relPath.replace(/\.md$/, '.html'));
          fs.mkdirSync(path.dirname(outRefHtmlPath), { recursive: true });
          fs.writeFileSync(outRefHtmlPath, refHtml);
          allReferencePages.push({
            url: `${skill.detailUrl}${res.relPath.replace(/\.md$/, '.html')}`,
            relPath: res.relPath,
            skill: skill.name
          });
        }
      }
    }
  }

  // Generate Category Landing Pages (e.g. /game-dev/, /writing/, etc.)
  for (const cat of CATEGORIES) {
    const catSkills = skills.filter(s => s.category === cat.id);
    const catHtml = generateCategoryHtml(cat, catSkills, CATEGORIES, skills);
    const catDir = path.join(SITE_DIR, cat.id);
    fs.mkdirSync(catDir, { recursive: true });
    fs.writeFileSync(path.join(catDir, 'index.html'), catHtml);
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
  llmsTxt += `## Optional\n\n`;
  llmsTxt += `- [Full Instructions Catalog](${DOMAIN}/llms-full.txt): Complete bundle of all 29 skill instructions in a single file for large-context models.\n`;
  llmsTxt += `- [Skills Catalog JSON](${DOMAIN}/catalog.json): Full machine-readable index conforming to the agentskills.io catalog schema.\n`;
  llmsTxt += `- [Fast Versions JSON](${DOMAIN}/versions.json): Lightweight hash and version validation index for JIT agent cache synchronization.\n`;
  fs.writeFileSync(path.join(SITE_DIR, 'llms.txt'), llmsTxt.trim() + '\n');
  fs.writeFileSync(path.join(ROOT_DIR, 'llms.txt'), llmsTxt.trim() + '\n');

  // 4. llms-full.txt
  let llmsFullTxt = `# danicat/skills (Full Instructions Catalog)\n\n> Complete collection of all Agent Skills.\n\n---\n\n`;
  for (const s of skills) {
    llmsFullTxt += `# Skill: ${s.name} (${s.category})\n\n> ${s.description}\n\n`;
    llmsFullTxt += `**Web Page**: ${s.detailUrl}\n**Source**: ${s.url}\n**Version**: ${s.version}\n**Digest**: ${s.digest}\n**Install**: \`${s.installCommand}\`\n\n`;
    llmsFullTxt += `## Instructions\n\n${s.body}\n\n---\n\n`;
  }
  fs.writeFileSync(path.join(SITE_DIR, 'llms-full.txt'), llmsFullTxt.trim() + '\n');

  // 5. catalog.json (agentskills.io schema)
  const catalog = {
    $schema: 'https://agentskills.io/schema/v1/catalog.json',
    name: 'danicat/skills',
    title: 'Daniela Petruzalek Agent Skills Catalog',
    description: 'A curated collection of specialized Agent Skills for coding, game development, generative media, writing, and engineering standards.',
    url: DOMAIN,
    repository: REPO_URL,
    totalSkills: skills.length,
    updatedAt: new Date().toISOString(),
    categories: CATEGORIES,
    gateway: {
      name: 'catalog',
      description: 'Dynamic search and loader for all skills in this repository.',
      url: `${DOMAIN}/SKILL.md`
    },
    items: skills.map(({ body, installCommand, npxInstallCommand, kungfuLoadCommand, kungfuLearnCommand, ...rest }) => ({
      ...rest,
      id: rest.name,
      type: 'skill',
      title: rest.name
    }))
  };
  const catalogJson = JSON.stringify(catalog, null, 2);
  fs.writeFileSync(path.join(SITE_DIR, 'catalog.json'), catalogJson);
  fs.writeFileSync(path.join(ROOT_DIR, 'catalog.json'), catalogJson);

  // 5b. versions.json (Ultra-lightweight fast check ~1.5 KB)
  const versionsObj = {
    updatedAt: new Date().toISOString(),
    totalSkills: skills.length,
    skills: {}
  };
  for (const s of skills) {
    versionsObj.skills[s.name] = {
      v: s.version,
      h: s.sha256.slice(0, 12),
      c: s.category,
      u: s.url
    };
  }
  const versionsJson = JSON.stringify(versionsObj, null, 2);
  fs.writeFileSync(path.join(SITE_DIR, 'versions.json'), versionsJson);
  fs.writeFileSync(path.join(ROOT_DIR, 'versions.json'), versionsJson);

  // 6. sitemap.xml
  let sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
  sitemapXml += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/SKILL.md</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/catalog.json</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/versions.json</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/llms.txt</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  sitemapXml += `  <url>\n    <loc>${DOMAIN}/llms-full.txt</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  for (const cat of CATEGORIES) {
    sitemapXml += `  <url>\n    <loc>${DOMAIN}/${cat.id}/</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.85</priority>\n  </url>\n`;
  }
  for (const s of skills) {
    // Detail page
    sitemapXml += `  <url>\n    <loc>${s.detailUrl}</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n`;
    // Raw SKILL.md
    sitemapXml += `  <url>\n    <loc>${s.url}</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n`;
  }
  for (const ref of allReferencePages) {
    sitemapXml += `  <url>\n    <loc>${ref.url}</loc>\n    <lastmod>${todayIso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.65</priority>\n  </url>\n`;
  }
  sitemapXml += `</urlset>\n`;
  fs.writeFileSync(path.join(SITE_DIR, 'sitemap.xml'), sitemapXml);

  // 7. robots.txt
  const robotsTxt = `User-agent: *\nAllow: /\n\nSitemap: ${DOMAIN}/sitemap.xml\n`;
  fs.writeFileSync(path.join(SITE_DIR, 'robots.txt'), robotsTxt);

  // 8. Catalog Home Page HTML
  const homeGraph = {
    '@context': 'https://schema.org',
    '@graph': [
      SCHEMA_AUTHOR,
      SCHEMA_PUBLISHER,
      {
        '@type': 'WebSite',
        '@id': `${DOMAIN}/#website`,
        url: `${DOMAIN}/`,
        name: 'danicat/skills',
        description: 'A curated collection of specialized Agent Skills for coding, game development, generative media, writing, and engineering standards.',
        publisher: { '@id': `${DOMAIN}/#organization` }
      },
      {
        '@type': 'CollectionPage',
        '@id': `${DOMAIN}/#catalog`,
        url: `${DOMAIN}/`,
        name: 'Agent Skills Catalog',
        isPartOf: { '@id': `${DOMAIN}/#website` },
        about: {
          '@type': 'ItemList',
          name: 'All Agent Skills',
          itemListElement: skills.map((s, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            name: s.name,
            description: s.description,
            url: s.detailUrl
          }))
        }
      }
    ]
  };

  const homeHtml = `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agent Skills · Daniela Petruzalek (danicat.dev)</title>
  <meta name="description" content="A curated collection of Agent Skills for 2D Go games, Python tooling, engineering standards, technical writing, and generative media.">
  <link rel="canonical" href="${DOMAIN}/">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="theme-color" content="#0f172a">
  <meta name="color-scheme" content="dark light">

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
  <meta property="og:site_name" content="Daniela Petruzalek (danicat.dev)">
  <meta property="og:image" content="${BLOG_URL}/apple-touch-icon.png">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Agent Skills · Daniela Petruzalek">
  <meta name="twitter:description" content="A curated collection of Agent Skills for 2D Go games, Python tooling, engineering standards, technical writing, and generative media.">
  <meta name="twitter:image" content="${BLOG_URL}/apple-touch-icon.png">
  <meta name="twitter:creator" content="@danicat83">

  <!-- JSON-LD Schema -->
  <script type="application/ld+json">
${JSON.stringify(homeGraph, null, 2)}
  </script>

  <link rel="icon" type="image/png" sizes="32x32" href="${BLOG_URL}/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="${BLOG_URL}/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="${BLOG_URL}/apple-touch-icon.png">

  <script>
    (function() {
      var appearance = localStorage.getItem('appearance');
      if (appearance === 'dark' || (!appearance && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.setAttribute('data-theme', 'light');
      }
    })();
  </script>
  <style>
${COMMON_CSS}

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
    }${ENABLE_KUNGFU ? `

    /* KungFu Home Feature Mode */
    .mode-pill {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.25rem 0.75rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-family: var(--font-mono);
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .mode-pill:hover {
      color: var(--text-heading);
      border-color: var(--border-hover);
    }
    .mode-pill.active {
      background: var(--badge-bg);
      border-color: var(--primary);
      color: var(--primary);
      font-weight: 600;
    }
    .install-tabs {
      display: flex;
      gap: 0.35rem;
      margin-bottom: -1px;
      position: relative;
      z-index: 1;
      flex-wrap: wrap;
    }
    .install-tab-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      border-bottom: none;
      border-radius: 6px 6px 0 0;
      padding: 0.35rem 0.75rem;
      font-size: 0.8rem;
      font-weight: 600;
      font-family: var(--font-mono);
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .install-tab-btn:hover {
      color: var(--text-heading);
      background: var(--code-bg);
    }
    .install-tab-btn.active {
      color: var(--primary);
      background: var(--code-bg);
      border-color: var(--code-border);
      border-bottom: 1px solid var(--code-bg);
    }` : ''}

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
  </style>
</head>
<body>
  <div class="container">
    ${renderHeader('Skills')}

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
        </div>${ENABLE_KUNGFU ? `
        <div class="install-tabs">
          <button type="button" class="install-tab-btn active" onclick="switchInstallTab(this, 'npx skills add danicat/skills -y')">npx skills add</button>
          <button type="button" class="install-tab-btn" onclick="switchInstallTab(this, 'kungfu load catalog')">kungfu load</button>
          <button type="button" class="install-tab-btn" onclick="switchInstallTab(this, 'kungfu learn catalog')">kungfu learn</button>
          <button type="button" class="install-tab-btn" onclick="switchInstallTab(this, 'https://skills.danicat.dev/SKILL.md')">Raw URL</button>
        </div>` : ''}
        <div class="gateway-install-box">
          <span class="gateway-cmd" id="gatewayCmdText">npx skills add danicat/skills -y</span>
          <button class="gateway-copy-btn" onclick="copyInstall(document.getElementById('gatewayCmdText').innerText, this)" title="Copy install command">
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
      </div>${ENABLE_KUNGFU ? `
      <div class="cli-mode-bar" style="display: flex; align-items: center; gap: 0.6rem; font-size: 0.85rem; color: var(--text-muted); margin-top: -0.25rem;">
        <span style="font-weight: 500;">CLI Mode:</span>
        <div class="cli-mode-pills" style="display: flex; gap: 0.35rem;">
          <button type="button" class="mode-pill active" onclick="setGlobalCliMode('npx', this)">npx skills</button>
          <button type="button" class="mode-pill" onclick="setGlobalCliMode('kungfu-load', this)">kungfu load</button>
          <button type="button" class="mode-pill" onclick="setGlobalCliMode('kungfu-learn', this)">kungfu learn</button>
          <button type="button" class="mode-pill" onclick="setGlobalCliMode('raw-url', this)">Raw URL</button>
        </div>
      </div>` : ''}
    </section>

    <main>
      <div class="skills-grid" id="skillsGrid">
        ${skills.map(s => `
        <div class="skill-card" data-category="${s.category}" data-name="${s.name.toLowerCase()}" data-desc="${s.description.toLowerCase().replace(/"/g, '&quot;')}">
          <div class="card-top">
            <div class="card-title-row">
              <a href="/${s.category}/${s.folder}/" class="skill-name-link">${s.name}</a>
              <span class="cat-badge">${s.categoryEmoji} ${s.categoryName}</span>
            </div>
            <p class="skill-description">${s.description}</p>
          </div>
          <div class="card-bottom">
            <div class="cmd-box" ${ENABLE_KUNGFU ? `data-npx="${escapeHtml(s.installCommand)}" data-kungfu-load="${escapeHtml(s.kungfuLoadCommand)}" data-kungfu-learn="${escapeHtml(s.kungfuLearnCommand)}" data-raw-url="${escapeHtml(s.url)}"` : ''}>
              <span class="cmd-text">${s.installCommand}</span>
              <button class="copy-button" onclick="copyInstall(this.previousElementSibling.innerText, this)" title="Copy install command">📋</button>
            </div>
            <div class="card-links">
              <a href="/${s.category}/${s.folder}/">View Skill →</a>
              <a href="/${s.relativePath}">Raw SKILL.md</a>
              <a href="${s.githubUrl}" target="_blank" rel="noopener">Source ↗</a>
            </div>
          </div>
        </div>`).join('')}
      </div>
    </main>

    ${renderFooter()}
  </div>

  <script>
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;

    function applyTheme(theme) {
      if (theme === 'dark') {
        htmlEl.classList.add('dark');
        htmlEl.setAttribute('data-theme', 'dark');
      } else {
        htmlEl.classList.remove('dark');
        htmlEl.setAttribute('data-theme', 'light');
      }
      localStorage.setItem('appearance', theme);
    }

    const savedTheme = localStorage.getItem('appearance') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(savedTheme);

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = htmlEl.classList.contains('dark') || htmlEl.getAttribute('data-theme') === 'dark';
        applyTheme(isDark ? 'light' : 'dark');
      });
    }

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

    function handleInitialCategory() {
      const hash = window.location.hash.replace(/^#/, '').toLowerCase().trim();
      const urlParams = new URLSearchParams(window.location.search);
      const catParam = urlParams.get('cat') || hash;
      if (catParam) {
        const targetBtn = document.querySelector('.pill-btn[data-cat="' + catParam + '"]');
        if (targetBtn) {
          pillButtons.forEach(b => b.classList.remove('active'));
          targetBtn.classList.add('active');
          activeCategory = catParam;
          filterSkills();
        }
      }
    }
    handleInitialCategory();
    window.addEventListener('hashchange', handleInitialCategory);

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
    }${ENABLE_KUNGFU ? `

    function switchInstallTab(btn, cmd) {
      btn.parentElement.querySelectorAll('.install-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cmdEl = document.getElementById('gatewayCmdText');
      if (cmdEl) cmdEl.innerText = cmd;
    }
    const switchGatewayTab = switchInstallTab;

    function setGlobalCliMode(mode, btn) {
      document.querySelectorAll('.mode-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      localStorage.setItem('preferred_cli_mode', mode);
      document.querySelectorAll('.cmd-box').forEach(box => {
        const textSpan = box.querySelector('.cmd-text');
        if (!textSpan) return;
        if (mode === 'kungfu-load') {
          textSpan.innerText = box.getAttribute('data-kungfu-load');
        } else if (mode === 'kungfu-learn') {
          textSpan.innerText = box.getAttribute('data-kungfu-learn');
        } else if (mode === 'raw-url') {
          textSpan.innerText = box.getAttribute('data-raw-url');
        } else {
          textSpan.innerText = box.getAttribute('data-npx');
        }
      });
    }

    const savedMode = localStorage.getItem('preferred_cli_mode');
    if (savedMode) {
      const modeBtn = document.querySelector('.mode-pill[onclick*="' + savedMode + '"]');
      if (modeBtn) setGlobalCliMode(savedMode, modeBtn);
    }` : ''}
  </script>
</body>
</html>`;

  fs.writeFileSync(path.join(SITE_DIR, 'index.html'), homeHtml);
  console.log(`Site build complete! Generated ${skills.length} skills detail pages, sitemap.xml, robots.txt, and assets in _site/.`);

  runAudit();
}

build().catch(err => {
  console.error(err);
  process.exit(1);
});
