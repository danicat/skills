# intro_who_is_it_for
Source: https://a2ui.org/introduction/who-is-it-for/

# Who is A2UI For?[¶](#who-is-a2ui-for "Permanent link")

Developers building AI agents with rich, interactive UIs.

## Three Audiences[¶](#three-audiences "Permanent link")

### 1. Host App Developers (Frontend)[¶](#1-host-app-developers-frontend "Permanent link")

Build multi-agent platforms, enterprise assistants, or cross-platform apps where agents generate UI.

**Why A2UI:**

* Brand control: client owns styling and design system.
* Multi-agent: support local, remote, and third-party agents.
* Secure: declarative data, no code execution.
* Cross-platform: web, mobile, desktop.
* Interoperable: open source, same spec with multiple renderers.

**Get started:** [Client Setup](../../guides/client-setup/) | [Theming](../../guides/theming/) | [Defining Your Own Catalog](../../guides/defining-your-own-catalog/)

### 2. Agent Developers (Backend/AI)[¶](#2-agent-developers-backendai "Permanent link")

Build agents that generate forms, dashboards, and interactive workflows.

**Why A2UI:**

* LLM-friendly: flat structure, easy to generate incrementally.
* Rich interactions: beyond text (forms, tables, visualizations).
* Generations not tools: UI as part of the generated output from the agent.
* Portable: one agent response works across all A2UI clients.
* Streamable: progressive rendering as you generate.

**Get started:** [Agent Development](../../guides/agent-development/)

### 3. Platform Builders (SDK Creators)[¶](#3-platform-builders-sdk-creators "Permanent link")

Build agent orchestration platforms, frameworks, or UI integrations.

Do you bring remote agents into your app?

Do you ship your agent into other apps you don't necessarily control?

**Why A2UI:**

* Standard protocol: interoperable with A2A and other transports.
* Extensible: custom component catalogs.
* Open source (Apache 2.0).

**Get started:** [Community](../../ecosystem/community/) | [Roadmap](../../roadmap/)

---

## When to Use A2UI[¶](#when-to-use-a2ui "Permanent link")

Use A2UI in the following scenarios:

* **Agent-generated UI**: Core purpose.
* **Multi-agent systems**: Standard protocol across trust boundaries.
* **Cross-platform apps**: One agent, many renderers (web/mobile/desktop).
* **Security critical**: Declarative data, no code execution.
* **Brand consistency**: Client controls styling.

Do not use A2UI for:

* **Static websites**: Use HTML/CSS.
* **Simple text-only chat**: Use Markdown.
* **Remote widgets not integrated with client**: Use iframes, like [MCP Apps](../agent-ui-ecosystem/).
* **Rapid UI + Agent app built together**: Use [AG-UI / CopilotKit](../agent-ui-ecosystem/).

See [Agent UI Ecosystem](../agent-ui-ecosystem/) for a detailed comparison.