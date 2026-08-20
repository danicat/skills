import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REFS_DIR = path.resolve(__dirname, '../agents/a2ui-developer-guide/references');

export function fixA2uiLinks() {
  if (!fs.existsSync(REFS_DIR)) return;

  const files = fs.readdirSync(REFS_DIR).filter(f => f.endsWith('.md'));

  const linkMappings = [
    // Direct concept mappings
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/concepts\/overview\/(#[^)]*)?\)/g, replacement: '[$1](./concept_overview.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/concepts\/overview\/(#[^)]*)?\)/g, replacement: '[$1](./concept_overview.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/overview\/(#[^)]*)?\)/g, replacement: '[$1](./concept_overview.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/concepts\/actions\/(#[^)]*)?\)/g, replacement: '[$1](./concept_actions.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/actions\/(#[^)]*)?\)/g, replacement: '[$1](./concept_actions.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/concepts\/catalogs\/(#[^)]*)?\)/g, replacement: '[$1](./concept_catalogs.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/catalogs\/(#[^)]*)?\)/g, replacement: '[$1](./concept_catalogs.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/concepts\/components\/(#[^)]*)?\)/g, replacement: '[$1](./concept_components.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/components\/(#[^)]*)?\)/g, replacement: '[$1](./concept_components.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/concepts\/data-binding\/(#[^)]*)?\)/g, replacement: '[$1](./concept_data_binding.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/data-binding\/(#[^)]*)?\)/g, replacement: '[$1](./concept_data_binding.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/concepts\/data-flow\/(#[^)]*)?\)/g, replacement: '[$1](./concept_data_flow.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/data-flow\/(#[^)]*)?\)/g, replacement: '[$1](./concept_data_flow.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/concepts\/glossary\/(#[^)]*)?\)/g, replacement: '[$1](./concept_glossary.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/glossary\/(#[^)]*)?\)/g, replacement: '[$1](./concept_glossary.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/concepts\/transports\/(#[^)]*)?\)/g, replacement: '[$1](./concept_transports.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/transports\/(#[^)]*)?\)/g, replacement: '[$1](./concept_transports.md$2)' },

    // Guides
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/a2ui-with-any-agent-framework\/(#[^)]*)?\)/g, replacement: '[$1](./guide_a2ui_with_any_agent_framework.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/guides\/a2ui-with-any-agent-framework\/(#[^)]*)?\)/g, replacement: '[$1](./guide_a2ui_with_any_agent_framework.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/a2ui-with-any-agent-framework\/(#[^)]*)?\)/g, replacement: '[$1](./guide_a2ui_with_any_agent_framework.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/defining-your-own-catalog\/(#[^)]*)?\)/g, replacement: '[$1](./guide_defining_own_catalog.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/defining-your-own-catalog\/(#[^)]*)?\)/g, replacement: '[$1](./guide_defining_own_catalog.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/agent-development\/(#[^)]*)?\)/g, replacement: '[$1](./guide_agent_development.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/guides\/agent-development\/(#[^)]*)?\)/g, replacement: '[$1](./guide_agent_development.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/agent-development\/(#[^)]*)?\)/g, replacement: '[$1](./guide_agent_development.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/client-setup\/(#[^)]*)?\)/g, replacement: '[$1](./guide_client_setup.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/guides\/client-setup\/(#[^)]*)?\)/g, replacement: '[$1](./guide_client_setup.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/client-setup\/(#[^)]*)?\)/g, replacement: '[$1](./guide_client_setup.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/authoring-components\/(#[^)]*)?\)/g, replacement: '[$1](./guide_authoring_components.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/authoring-components\/(#[^)]*)?\)/g, replacement: '[$1](./guide_authoring_components.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/mcp-integration\/(#[^)]*)?\)/g, replacement: '[$1](./guide_mcp_integration.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/mcp-integration\/(#[^)]*)?\)/g, replacement: '[$1](./guide_mcp_integration.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/mcp-apps-in-a2ui\/(#[^)]*)?\)/g, replacement: '[$1](./guide_mcp_integration.md#mcp-apps-in-a2ui-surface)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/a2ui_over_mcp\/(#[^)]*)?\)/g, replacement: '[$1](./guide_mcp_integration.md#a2ui-over-mcp)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/quickstart\/(#[^)]*)?\)/g, replacement: '[$1](./guide_quickstart.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/quickstart\/(#[^)]*)?\)/g, replacement: '[$1](./guide_quickstart.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/quickstart\/(#[^)]*)?\)/g, replacement: '[$1](./guide_quickstart.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/renderer-development\/(#[^)]*)?\)/g, replacement: '[$1](./guide_renderer_development.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/renderer-development\/(#[^)]*)?\)/g, replacement: '[$1](./guide_renderer_development.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/guides\/theming\/(#[^)]*)?\)/g, replacement: '[$1](./guide_theming.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/theming\/(#[^)]*)?\)/g, replacement: '[$1](./guide_theming.md$2)' },

    // Intro & Ecosystem
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/intro\/what-is-a2ui\/(#[^)]*)?\)/g, replacement: '[$1](./intro_what_is_a2ui.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/what-is-a2ui\/(#[^)]*)?\)/g, replacement: '[$1](./intro_what_is_a2ui.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/intro\/ecosystem\/(#[^)]*)?\)/g, replacement: '[$1](./intro_ecosystem.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/ecosystem\/(#[^)]*)?\)/g, replacement: '[$1](./intro_ecosystem.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/agent-ui-ecosystem\/(#[^)]*)?\)/g, replacement: '[$1](./intro_ecosystem.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/intro\/how-to-use\/(#[^)]*)?\)/g, replacement: '[$1](./intro_how_to_use.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/how-to-use\/(#[^)]*)?\)/g, replacement: '[$1](./intro_how_to_use.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/ecosystem\/renderers\/(#[^)]*)?\)/g, replacement: '[$1](./ecosystem_renderers.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/renderers\/(#[^)]*)?\)/g, replacement: '[$1](./ecosystem_renderers.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/ecosystem\/a2ui-in-the-world\/(#[^)]*)?\)/g, replacement: '[$1](https://a2ui.org/ecosystem/a2ui-in-the-world/)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/composer\/(#[^)]*)?\)/g, replacement: '[$1](https://a2ui.org/composer/)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/roadmap\/(#[^)]*)?\)/g, replacement: '[$1](https://a2ui.org/roadmap/)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/examples\/open-source-examples\/(#[^)]*)?\)/g, replacement: '[$1](./open_source_examples.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/open-source-examples\/(#[^)]*)?\)/g, replacement: '[$1](./open_source_examples.md$2)' },

    // References & Specs
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/reference\/components\/(#[^)]*)?\)/g, replacement: '[$1](./ref_components.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/reference\/messages\/(#[^)]*)?\)/g, replacement: '[$1](./ref_messages.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/reference\/messages\/(#[^)]*)?\)/g, replacement: '[$1](./ref_messages.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/reference\/renderers\/(#[^)]*)?\)/g, replacement: '[$1](./ecosystem_renderers.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/reference\/agents\/(#[^)]*)?\)/g, replacement: '[$1](./ref_sdks.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/agents\/(#[^)]*)?\)/g, replacement: '[$1](./ref_sdks.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/reference\/sdks\/(#[^)]*)?\)/g, replacement: '[$1](./ref_sdks.md$2)' },

    // JSON schemas and catalogs
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v0_9_1\/catalogs\/basic\/catalog\.json(#[^)]*)?\)/g, replacement: '[$1](./schema_v0.9.1_catalog.json$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v1_0\/catalogs\/basic\/catalog\.json(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_basic_catalog.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v0_9\/json\/common_types\.json(#[^)]*)?\)/g, replacement: '[$1](./schema_v0.9_common_types.json$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/v0_9_1\/json\/client_data_model\.json(#[^)]*)?\)/g, replacement: '[$1](./schema_v0.9.1_client_data_model.json$2)' },

    // Specs
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v0\.8-a2a-extension\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_extension.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v0\.9\.1-a2a-extension\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_extension.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v0\.9-a2ui\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_core.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v0\.9\.1-a2ui\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_core.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/v0\.8-a2ui\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_core.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/v0\.9-a2ui\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_core.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/v0\.9\.1-a2ui\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_core.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/v0\.9\.1-evolution-guide\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_evolution.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v0\.9\.1-evolution-guide\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_evolution.md$2)' },
    { regex: /\[([^\]]*?)\]\(\.\.\/\.\.\/specification\/v0\.9\.1-basic-catalog\/(#[^)]*)?\)/g, replacement: '[$1](./spec_v0.9.1_basic_catalog.md$2)' },

    // Assets / Images
    { regex: /!\[(.*?)\]\(\.\.\/\.\.\/\.\.\/assets\/(.*?)\)/g, replacement: '![$1](https://a2ui.org/assets/$2)' },
    { regex: /!\[(.*?)\]\(\.\.\/\.\.\/assets\/(.*?)\)/g, replacement: '![$1](https://a2ui.org/assets/$2)' },
    { regex: /!\[(.*?)\]\(\.\.\/assets\/(.*?)\)/g, replacement: '![$1](https://a2ui.org/assets/$2)' },

    // Strip MkDocs permalink characters [¶](#anchor "Permanent link")
    { regex: /\[¶\]\([^)]+\)/g, replacement: '' }
  ];

  for (const file of files) {
    const fullPath = path.join(REFS_DIR, file);
    let content = fs.readFileSync(fullPath, 'utf8');
    let original = content;

    for (const mapping of linkMappings) {
      content = content.replace(mapping.regex, (match, ...args) => {
        let res = mapping.replacement;
        for (let i = 0; i < args.length; i++) {
          const val = args[i] || '';
          res = res.replace(new RegExp(`\\$${i + 1}`, 'g'), val);
        }
        return res;
      });
    }

    if (content !== original) {
      fs.writeFileSync(fullPath, content, 'utf8');
    }
  }
}
