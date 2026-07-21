# intro_how_to_use
Source: https://a2ui.org/introduction/how-to-use/

# How to Use A2UI[¶](#how-to-use-a2ui "Permanent link")

Choose the integration path that matches your role and use case.

## Three Paths[¶](#three-paths "Permanent link")

### Path 1: Building a Host Application (Frontend)[¶](#path-1-building-a-host-application-frontend "Permanent link")

Integrate A2UI rendering into your existing app or build a new agent-powered frontend.

**Choose a renderer:**

* **Web:** Lit, Angular, React.
* **Mobile/Desktop:** Flutter GenUI SDK.

**Quick setup:**

For Angular:

```
npm install @a2ui/angular @a2ui/web_core
```

For React:

```
npm install @a2ui/react @a2ui/web_core
```

Connect to agent messages (SSE, WebSockets, or A2A) and customize styling to match your brand.

**Next:** [Client Setup Guide](../../guides/client-setup/) | [Theming](../../guides/theming/)

---

### Path 2: Building an Agent (Backend)[¶](#path-2-building-an-agent-backend "Permanent link")

Create an agent that generates A2UI responses for any compatible client.

**Choose your framework:**

* **Python:** Google ADK, LangChain, custom.
* **Node.js:** A2A SDK, Vercel AI SDK, custom.

Include the A2UI schema in your LLM prompts, generate JSONL messages, and stream to clients over SSE, WebSockets, or A2A.

**Next:** [Agent Development Guide](../../guides/agent-development/)

---

### Path 3: Using an Existing Framework[¶](#path-3-using-an-existing-framework "Permanent link")

Use A2UI through frameworks with built-in support:

* **[AG-UI / CopilotKit](https://ag-ui.com/)** - Full-stack agentic app framework with A2UI rendering.
* **[Flutter GenUI SDK](https://docs.flutter.dev/ai/genui)** - Cross-platform generative UI (uses A2UI internally).

**Next:** [Agent UI Ecosystem](../agent-ui-ecosystem/) | [Where is A2UI Used?](../../ecosystem/a2ui-in-the-world/)