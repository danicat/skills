import fs from 'fs';
import path from 'path';
import vm from 'vm';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const SITE_DIR = path.resolve(ROOT_DIR, '_site');

export function runAudit() {
  console.log('\n========================================');
  console.log('=== QA AUDIT & LINK INTEGRITY REPORT ===');
  console.log('========================================\n');

  function getAllFiles(dir, exts = []) {
    let results = [];
    if (!fs.existsSync(dir)) return results;
    const list = fs.readdirSync(dir);
    for (const file of list) {
      const fullPath = path.resolve(dir, file);
      const stat = fs.statSync(fullPath);
      if (stat && stat.isDirectory()) {
        if (file !== 'node_modules' && file !== '.git') {
          results = results.concat(getAllFiles(fullPath, exts));
        }
      } else {
        if (exts.length === 0 || exts.some(ext => file.endsWith(ext))) {
          results.push(fullPath);
        }
      }
    }
    return results;
  }

  const htmlFiles = getAllFiles(SITE_DIR, ['.html']);
  const mdFiles = getAllFiles(ROOT_DIR, ['.md']).filter(f => !f.includes('/_site/'));

  let htmlErrors = [];
  let mdErrors = [];
  let assetErrors = [];
  let warnings = [];
  let uiIssues = [];

  // 1. Root Assets
  const requiredRootAssets = ['CNAME', 'index.html', 'llms.txt', 'llms-full.txt', 'catalog.json', 'versions.json', 'sitemap.xml', 'robots.txt'];
  for (const asset of requiredRootAssets) {
    if (!fs.existsSync(path.join(SITE_DIR, asset))) {
      assetErrors.push(`[Root Asset Missing] Missing required site asset: _site/${asset}`);
    }
  }

  // 2. HTML Files
  let totalHtmlLinksChecked = 0;
  let totalHtmlAssetsChecked = 0;

  for (const file of htmlFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const relFile = path.relative(SITE_DIR, file);

    // Check <a href="...">
    const aHrefRegex = /<a\s+[^>]*?href=["']([^"']+)["'][^>]*?>/gi;
    let match;
    while ((match = aHrefRegex.exec(content)) !== null) {
      totalHtmlLinksChecked++;
      const href = match[1];

      if (href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) {
        continue;
      }
      if (href.startsWith('http://') || href.startsWith('https://')) {
        if (href.startsWith('https://skills.danicat.dev/')) {
          const urlPath = href.replace('https://skills.danicat.dev/', '').split('#')[0].split('?')[0];
          const targetPath = path.resolve(SITE_DIR, urlPath);
          if (!fs.existsSync(targetPath) && !fs.existsSync(targetPath + '.html') && !fs.existsSync(path.join(targetPath, 'index.html'))) {
            htmlErrors.push(`[HTML Link 404] In ${relFile}: absolute site link "${href}" does not exist on disk`);
          }
        }
        continue;
      }

      if (href.startsWith('#')) {
        const anchorId = href.substring(1);
        if (anchorId) {
          const idRegex = new RegExp(`id=["']${anchorId}["']|name=["']${anchorId}["']`, 'i');
          if (!idRegex.test(content)) {
            warnings.push(`[HTML Anchor Warning] In ${relFile}: anchor #${anchorId} not found in file`);
          }
        }
        continue;
      }

      const [urlPath, anchor] = href.split('#');
      const cleanUrl = urlPath.split('?')[0];

      if (!cleanUrl && anchor) {
        continue;
      }

      let resolvedPath;
      if (cleanUrl.startsWith('/')) {
        resolvedPath = path.resolve(SITE_DIR, '.' + cleanUrl);
      } else {
        resolvedPath = path.resolve(path.dirname(file), cleanUrl);
      }

      let exists = false;
      if (fs.existsSync(resolvedPath)) {
        const stat = fs.statSync(resolvedPath);
        if (stat.isDirectory()) {
          if (fs.existsSync(path.join(resolvedPath, 'index.html'))) {
            exists = true;
          }
        } else {
          exists = true;
        }
      } else if (fs.existsSync(resolvedPath + '.html')) {
        exists = true;
      }

      if (!exists) {
        htmlErrors.push(`[HTML Link 404] In ${relFile}: link "${href}" -> resolved to non-existent "${path.relative(SITE_DIR, resolvedPath)}"`);
      }
    }

    // Check <link href="...">
    const linkTagRegex = /<link\s+[^>]*?href=["']([^"']+)["'][^>]*?>/gi;
    while ((match = linkTagRegex.exec(content)) !== null) {
      totalHtmlAssetsChecked++;
      const href = match[1];
      if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('//')) {
        continue;
      }
      const cleanUrl = href.split('?')[0];
      let resolvedPath = cleanUrl.startsWith('/') ? path.resolve(SITE_DIR, '.' + cleanUrl) : path.resolve(path.dirname(file), cleanUrl);
      if (!fs.existsSync(resolvedPath)) {
        assetErrors.push(`[HTML Asset 404] In ${relFile}: <link> stylesheet/icon "${href}" does not exist`);
      }
    }

    // Check <script src="...">
    const scriptTagRegex = /<script\s+[^>]*?src=["']([^"']+)["'][^>]*?>/gi;
    while ((match = scriptTagRegex.exec(content)) !== null) {
      totalHtmlAssetsChecked++;
      const src = match[1];
      if (src.startsWith('http://') || src.startsWith('https://') || src.startsWith('//')) {
        continue;
      }
      const cleanUrl = src.split('?')[0];
      let resolvedPath = cleanUrl.startsWith('/') ? path.resolve(SITE_DIR, '.' + cleanUrl) : path.resolve(path.dirname(file), cleanUrl);
      if (!fs.existsSync(resolvedPath)) {
        assetErrors.push(`[HTML Asset 404] In ${relFile}: <script> "${src}" does not exist`);
      }
    }

    // Check <img src="...">
    const imgTagRegex = /<img\s+[^>]*?src=["']([^"']+)["'][^>]*?>/gi;
    while ((match = imgTagRegex.exec(content)) !== null) {
      totalHtmlAssetsChecked++;
      const src = match[1];
      if (src.startsWith('data:') || src.startsWith('http://') || src.startsWith('https://')) {
        continue;
      }
      const cleanUrl = src.split('?')[0];
      let resolvedPath = cleanUrl.startsWith('/') ? path.resolve(SITE_DIR, '.' + cleanUrl) : path.resolve(path.dirname(file), cleanUrl);
      if (!fs.existsSync(resolvedPath)) {
        assetErrors.push(`[HTML Asset 404] In ${relFile}: <img> "${src}" does not exist`);
      }
    }

    // Check <meta property="og:image" content="...">
    const ogImgRegex = /<meta\s+[^>]*?property=["']og:image["'][^>]*?content=["']([^"']+)["'][^>]*?>/gi;
    while ((match = ogImgRegex.exec(content)) !== null) {
      totalHtmlAssetsChecked++;
      const contentVal = match[1];
      if (contentVal.startsWith('https://skills.danicat.dev/')) {
        const assetPath = contentVal.replace('https://skills.danicat.dev/', '').split('?')[0];
        const resolvedPath = path.resolve(SITE_DIR, assetPath);
        if (!fs.existsSync(resolvedPath)) {
          assetErrors.push(`[HTML og:image 404] In ${relFile}: og:image "${contentVal}" does not exist on disk`);
        }
      }
    }

    // UI Interactivity Checks
    if (content.includes('id="themeToggle"')) {
      if (!content.includes('themeToggle') || (!content.includes('localStorage.getItem(\'appearance\')') && !content.includes('localStorage.getItem(\'theme\')'))) {
        uiIssues.push(`[UI Theme Toggle] In ${relFile}: #themeToggle present but script logic incomplete`);
      }
    }

    if (content.includes('class="install-tabs"')) {
      if (!content.includes('function switchInstallTab')) {
        uiIssues.push(`[UI Tab Switching] In ${relFile}: install-tabs present but switchInstallTab() missing`);
      }
    }

    if (content.includes('copy-install-btn') || content.includes('onclick="copyInstall(')) {
      if (!content.includes('function copyInstall') && !content.includes('copyInstall(')) {
        uiIssues.push(`[UI Copy Button] In ${relFile}: copy-install-btn present but copyInstall logic missing`);
      }
    }

    if (content.includes('class="copy-code-btn"')) {
      if (!content.includes('function copySnippet') && !content.includes('navigator.clipboard.writeText')) {
        uiIssues.push(`[UI Copy Snippet] In ${relFile}: copy-code-btn present but copySnippet logic missing`);
      }
    }

    // Inline JavaScript Syntax Validation
    const inlineScriptRegex = /<script(?![^>]*?src=)([^>]*?)>([\s\S]*?)<\/script>/gi;
    let scriptMatch;
    while ((scriptMatch = inlineScriptRegex.exec(content)) !== null) {
      const tagAttrs = scriptMatch[1] || '';
      const scriptCode = scriptMatch[2].trim();
      if (!scriptCode || tagAttrs.includes('application/ld+json')) continue;
      try {
        const codeToTest = tagAttrs.includes('module')
          ? scriptCode.replace(/import\s+[\s\S]*?from\s+['"][^'"]+['"];?/g, '// import')
          : scriptCode;
        new vm.Script(codeToTest);
      } catch (err) {
        uiIssues.push(`[JS Syntax Error] In ${relFile}: Inline script syntax error: ${err.message}`);
      }
    }
  }

  // 3. Markdown Files
  let totalMdLinksChecked = 0;

  for (const file of mdFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const relFile = path.relative(ROOT_DIR, file);

    const mdLinkRegex = /\[([^\]]*?)\]\(([^)]+)\)/g;
    let match;
    while ((match = mdLinkRegex.exec(content)) !== null) {
      totalMdLinksChecked++;
      const label = match[1];
      const url = match[2].trim();

      if (url.includes('<em>') || url.includes('</em>') || url.includes('<strong>')) {
        mdErrors.push(`[Markdown Corrupted Link] In ${relFile}: link url "${url}" contains HTML tag (e.g. <em>)`);
      }

      if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('mailto:') || url.startsWith('conversation:') || url.startsWith('file:')) {
        continue;
      }

      // Template shortcodes or special doc placeholders
      if (url.includes('{{<') || url.startsWith('...') || url === '#') {
        continue;
      }

      if (url.startsWith('#')) {
        continue;
      }

      const cleanUrl = url.split('#')[0].split('?')[0];
      if (!cleanUrl) continue;

      const resolvedPath = cleanUrl.startsWith('/') ? path.resolve(ROOT_DIR, '.' + cleanUrl) : path.resolve(path.dirname(file), cleanUrl);

      if (!fs.existsSync(resolvedPath)) {
        mdErrors.push(`[Markdown Link 404] In ${relFile}: link [${label}](${url}) -> "${path.relative(ROOT_DIR, resolvedPath)}" does not exist`);
      }
    }

    const rawHtmlTagRegex = /<a\s+[^>]*?href=["']([^"']+)["'][^>]*?>/gi;
    while ((match = rawHtmlTagRegex.exec(content)) !== null) {
      totalMdLinksChecked++;
      const href = match[1];
      if (href.includes('<em>') || href.includes('</em>')) {
        mdErrors.push(`[Markdown Corrupted HTML Tag] In ${relFile}: <a href="${href}"> contains <em> tag`);
      }
    }
  }

  console.log(`Verified ${totalHtmlLinksChecked} HTML links across ${htmlFiles.length} HTML files.`);
  console.log(`Verified ${totalHtmlAssetsChecked} static asset references across ${htmlFiles.length} HTML files.`);
  console.log(`Verified ${totalMdLinksChecked} Markdown links across ${mdFiles.length} source markdown files.`);

  console.log('\n=== SUMMARY BREAKDOWN ===');
  console.log(`HTML Link Errors (404s): ${htmlErrors.length}`);
  console.log(`Asset Errors (404 stylesheets/scripts/images): ${assetErrors.length}`);
  console.log(`Markdown Link Errors (404 / corrupted <em>): ${mdErrors.length}`);
  console.log(`UI Issues: ${uiIssues.length}`);
  console.log(`Anchor Warnings: ${warnings.length}`);

  if (htmlErrors.length > 0) {
    console.log(`\n--- HTML LINK ERRORS (${htmlErrors.length}) ---`);
    htmlErrors.slice(0, 30).forEach((e, i) => console.log(`${i + 1}. ${e}`));
    if (htmlErrors.length > 30) console.log(`... and ${htmlErrors.length - 30} more HTML link errors.`);
  }

  if (assetErrors.length > 0) {
    console.log(`\n--- ASSET ERRORS (${assetErrors.length}) ---`);
    assetErrors.forEach((e, i) => console.log(`${i + 1}. ${e}`));
  }

  if (mdErrors.length > 0) {
    console.log(`\n--- MARKDOWN LINK ERRORS (${mdErrors.length}) ---`);
    mdErrors.slice(0, 30).forEach((e, i) => console.log(`${i + 1}. ${e}`));
    if (mdErrors.length > 30) console.log(`... and ${mdErrors.length - 30} more Markdown link errors.`);
  }

  if (uiIssues.length > 0) {
    console.log(`\n--- UI ISSUES (${uiIssues.length}) ---`);
    uiIssues.slice(0, 30).forEach((e, i) => console.log(`${i + 1}. ${e}`));
    if (uiIssues.length > 30) console.log(`... and ${uiIssues.length - 30} more UI issues.`);
  }

  if (htmlErrors.length === 0 && assetErrors.length === 0 && mdErrors.length === 0 && uiIssues.length === 0) {
    console.log('\n✓ ZERO 404s, ZERO BROKEN ASSETS, ZERO BROKEN LINKS, ALL UI SCRIPTS PASSING!');
  }

  return { htmlErrors, assetErrors, mdErrors, warnings, uiIssues, htmlFilesCount: htmlFiles.length, mdFilesCount: mdFiles.length };
}
