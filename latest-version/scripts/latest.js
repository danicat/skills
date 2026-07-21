#!/usr/bin/env node

/**
 * latest-version/scripts/latest.js
 * 
 * Fetches the latest stable version of a package from official registries.
 * Usage: node latest.js <ecosystem> <package_name1> [package_name2]... [--json]
 * 
 * Ecosystems: npm, pypi, go, cargo, gem, gemini
 */

const https = require('https');

let isJson = false;
let rawArgs = process.argv.slice(2);
if (rawArgs.includes('--json')) {
  isJson = true;
  rawArgs = rawArgs.filter(a => a !== '--json');
}

const args = rawArgs;
if (args.length < 2) {
  if (isJson) {
    console.log(JSON.stringify([{ error: "Usage: node latest.js <ecosystem> <package_name1> [package_name2]... [--json]" }]));
  } else {
    console.error("Usage: node latest.js <ecosystem> <package_name1> [package_name2]... [--json]");
    console.error("Supported: npm, pypi, go, cargo, gem, gemini");
  }
  process.exit(1);
}

const ecosystem = args[0];
const packages = args.slice(1);

function fetchJSON(url, parseJson = true) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Gemini-CLI-Version-Checker' } }, (res) => {
      let data = '';
      if (res.statusCode >= 400) {
        reject(new Error(`Registry returned ${res.statusCode}`));
        return;
      }
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          if (parseJson) {
            resolve(JSON.parse(data));
          } else {
            resolve(data);
          }
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function resolvePackage(ecosystem, pkg) {
  try {
    switch (ecosystem.toLowerCase()) {
      case 'npm': {
        const npmData = await fetchJSON(`https://registry.npmjs.org/${pkg}`);
        const npmLatest = npmData['dist-tags']?.latest;
        if (!npmLatest) throw new Error("No latest tag found");
        
        const result = { version: npmLatest, warnings: [], notes: [] };
        const npmVerData = npmData.versions[npmLatest];
        if (npmVerData && npmVerData.deprecated) {
          result.warnings.push(`This package is deprecated! Reason: "${npmVerData.deprecated}"`);
        }
        return result;
      }

      case 'pypi': {
        const pypiData = await fetchJSON(`https://pypi.org/pypi/${pkg}/json`);
        const pypiLatest = pypiData.info.version;
        const result = { version: pypiLatest, warnings: [], notes: [] };
        
        if (pypiData.info.yanked) {
          result.warnings.push(`This release was YANKED. Reason: "${pypiData.info.yanked_reason}"`);
        }
        if (pypiData.info.classifiers && pypiData.info.classifiers.includes("Development Status :: 7 - Inactive")) {
          result.warnings.push("This package is marked as Inactive.");
        }
        return result;
      }

      case 'go': {
        // Correct Go proxy capitalization encoding: uppercase letters replaced with !lowercase_letter
        const encodedPkg = pkg.replace(/[A-Z]/g, match => '!' + match.toLowerCase());
        const goData = await fetchJSON(`https://proxy.golang.org/${encodedPkg}/@latest`);
        const result = { version: goData.Version, warnings: [], notes: [] };

        if (goData.Retracted) {
          result.warnings.push(`This version (${goData.Version}) is RETRACTED!`);
        }
        
        if (pkg.startsWith("github.com/")) {
          const repoPath = pkg.replace("github.com/", "");
          try {
            const repoData = await fetchJSON(`https://api.github.com/repos/${repoPath}`);
            if (repoData) {
              if (repoData.archived) {
                result.warnings.push(`GitHub repository '${repoPath}' is ARCHIVED.`);
              } else {
                const desc = (repoData.description || "").toLowerCase();
                if (desc.includes("deprecated") || desc.includes("moved to")) {
                  result.warnings.push(`Potential deprecation/move detected in description: "${repoData.description}"`);
                }

                const readmeData = await fetchJSON(`https://api.github.com/repos/${repoPath}/readme`);
                if (readmeData && readmeData.content) {
                  const content = Buffer.from(readmeData.content, 'base64').toString('utf8').toLowerCase();
                  if (content.includes("deprecated") || content.includes("use google.golang.org/genai")) {
                    result.warnings.push(`The README for '${repoPath}' indicates this package is DEPRECATED or superseded.`);
                  }
                }
              }
            }
          } catch (e) {}
        }
        return result;
      }

      case 'cargo': {
        const cargoData = await fetchJSON(`https://crates.io/api/v1/crates/${pkg}`);
        return { version: cargoData.crate.max_stable_version, warnings: [], notes: [] };
      }
      
      case 'gem': {
        const gemData = await fetchJSON(`https://rubygems.org/api/v1/versions/${pkg}/latest.json`);
        return { version: gemData.version, warnings: [], notes: [] };
      }

      case 'gemini': {
        const sources = [
          'https://ai.google.dev/gemini-api/docs/models.md.txt',
          'https://ai.google.dev/gemini-api/docs/image-generation.md.txt'
        ];
        
        let allModels = [];
        let brandNames = {};

        for (const url of sources) {
          const text = await fetchJSON(url, false);
          
          const regex1 = /\[###\s+([^\]\n]+)[\s\S]*?\]\(https:\/\/ai\.google\.dev\/gemini-api\/docs\/models\/([^)]+)\)/g;
          for (const match of text.matchAll(regex1)) {
            const brand = match[1].trim();
            const modelId = match[2].trim();
            allModels.push(modelId);
            brandNames[brand] = modelId;
          }

          const regex2 = /###\s+\[([^\]]+)\]\(https:\/\/ai\.google\.dev\/gemini-api\/docs\/models\/([^)]+)\)/g;
          for (const match of text.matchAll(regex2)) {
            const brand = match[1].trim();
            const modelId = match[2].trim();
            allModels.push(modelId);
            brandNames[brand] = modelId;
          }

          const codeMatch = text.match(/`gemini-[^`]+`/gi);
          if (codeMatch) {
            allModels.push(...codeMatch.map(m => m.replace(/`/g, '')));
          }

          const brandMatches = text.matchAll(/-\s+\*\*(.*?)\*\*\s+:\s+.*?`([^`]+)`/g);
          for (const match of brandMatches) {
            const brand = match[1].trim(); 
            const modelId = match[2].trim(); 
            brandNames[brand] = modelId;
          }
        }

        const uniqueModels = [...new Set(allModels)].sort((a, b) => {
          const va = a.match(/\d+(\.\d+)?/)?.[0] || '0';
          const vb = b.match(/\d+(\.\d+)?/)?.[0] || '0';
          return parseFloat(vb) - parseFloat(va);
        });

        const target = pkg.toLowerCase().replace(/\s+/g, '');
        const matchingBrands = Object.keys(brandNames).filter(b => 
          b.toLowerCase().replace(/\s+/g, '').includes(target)
        );
        
        if (matchingBrands.length > 0) {
          const primaryBrand = matchingBrands[0];
          const primaryModel = brandNames[primaryBrand];
          const notes = matchingBrands.slice(1).map(brand => `Also found brand: ${brand} @ ${brandNames[brand]}`);
          return { version: primaryModel, warnings: [], notes: [`Brand Name: ${primaryBrand}`, ...notes] };
        }

        let results = uniqueModels;
        if (target !== 'latest' && target !== 'all') {
          results = uniqueModels.filter(m => m.includes(target));
        }

        if (results.length > 0) {
          const notes = [];
          if (results.length > 1) {
            notes.push(`Also found: ${results.slice(1, 5).join(', ')}`);
          }
          return { version: results[0], warnings: [], notes };
        } else {
          return { 
            version: null, 
            warnings: [], 
            notes: [
              `Known brands: ${Object.keys(brandNames).join(', ')}`,
              `Latest codes: ${uniqueModels.slice(0, 3).join(', ')}`
            ],
            error: `No models found matching "${pkg}".`
          };
        }
      }

      default:
        return { version: null, warnings: [], notes: [], error: `Unknown ecosystem: ${ecosystem}` };
    }
  } catch (err) {
    return { version: null, warnings: [], notes: [], error: err.message };
  }
}

async function main() {
  const results = [];
  for (const pkg of packages) {
    const res = await resolvePackage(ecosystem, pkg);
    results.push({
      ecosystem: ecosystem.toLowerCase(),
      package: pkg,
      version: res.version,
      warnings: res.warnings || [],
      notes: res.notes || [],
      error: res.error || null
    });
  }

  if (isJson) {
    console.log(JSON.stringify(results, null, 2));
  } else {
    for (const res of results) {
      if (res.error) {
        console.error(`❌ Error fetching version for ${res.package}: ${res.error}`);
        continue;
      }
      console.log(`${res.ecosystem}: ${res.package} @ ${res.version}`);
      for (const warning of res.warnings) {
        console.log(`⚠️  WARNING: ${warning}`);
      }
      for (const note of res.notes) {
        console.log(`ℹ️  Note: ${note}`);
      }
    }
  }
  
  const allFailed = results.length > 0 && results.every(r => r.error !== null);
  if (allFailed) {
    process.exit(1);
  }
}

main();
