---
name: a2ui_developer_guide
description: A comprehensive developer guide containing the entire a2ui.org documentation suite. Contains full specs for A2UI v0.9.1, JSON schemas, Agent (Python/ADK) & Renderer (React/Angular/Flutter) SDK guides, concept definitions, quickstarts, and open-source examples. Use this for ANY question or coding task related to Agent-Driven User Interfaces.
---

# A2UI Developer Guide

This skill serves as the ultimate, comprehensive reference for developing applications, agents, and client libraries using the **A2UI (Agent-Driven User Interfaces) Protocol**. 

A2UI is a streaming protocol designed to allow Agents to emit rich, interactive UI components directly into the chat stream.

## Core Mandates
When working with A2UI, you MUST consult the reference documentation provided in the `references/` directory. Do not guess the structure of the JSON payload, the client data models, or the expected component formats. Always verify against the spec.

## Reference Material
All references have been crawled directly from the official [A2UI.org](https://a2ui.org) documentation and converted to markdown. They are located in the `references/` directory of this skill. 

Use the `view_file` tool to read the contents of the relevant reference file before responding:

### 1. Introduction
*   [What is A2UI?](references/intro_what_is_a2ui.md)
*   [Who is it for?](references/intro_who_is_it_for.md)
*   [How to use it](references/intro_how_to_use.md)
*   [Agent UI Ecosystem](references/intro_ecosystem.md)

### 2. Core Concepts
*   [Overview](references/concept_overview.md)
*   [Components](references/concept_components.md)
*   [Data Flow](references/concept_data_flow.md)
*   [Data Binding](references/concept_data_binding.md)
*   [Catalogs](references/concept_catalogs.md)
*   [Transports](references/concept_transports.md)
*   [Actions](references/concept_actions.md)
*   [Glossary](references/concept_glossary.md)

### 3. Implementation Guides & Tutorials
*   [Quickstart](references/guide_quickstart.md): The fastest path to getting a basic A2UI application running.
*   [Client Setup](references/guide_client_setup.md): Consume the A2UI protocol on the frontend (React, Angular, Lit, etc.).
*   [Agent Development](references/guide_agent_development.md): Build Agents that emit A2UI components using Python/ADK.
*   [Defining Your Own Catalog](references/guide_defining_own_catalog.md): Build custom catalogs matching your design system.
*   [Authoring Components](references/guide_authoring_components.md): Create new interactive UI components for agents to use.
*   [Theming](references/guide_theming.md): Styling and theming A2UI components.
*   [Renderer Development](references/guide_renderer_development.md): Build custom renderers for interpreting A2UI.
*   [A2UI with Any Agent Framework](references/guide_a2ui_with_any_agent_framework.md): Using A2UI with LangChain, LlamaIndex, etc.
*   [A2UI in MCP Apps](references/guide_a2ui_in_mcp_apps.md) & [A2UI over MCP](references/guide_a2ui_over_mcp.md): Integrating with the Model Context Protocol.

### 4. SDKs and Reference
*   [Messages](references/ref_messages.md): Full reference of valid A2UI protocol messages.
*   [Components](references/ref_components.md): Standard components reference.
*   [Renderers SDK Reference (React, Angular, Lit, Flutter)](references/ref_renderers.md): Frontend Client Libraries reference.
*   [Agents SDK Reference (Python/ADK)](references/ref_agents.md): Server-side agent reference.

### 5. Specifications & Protocol (v0.9.1)
*   [v0.9.1 Core Specification](references/spec_v0.9.1_core.md): The absolute source of truth for the A2UI v0.9.1 data models, JSON schemas, component states, and messaging.
*   [v0.9.1 Extension Specification](references/spec_v0.9.1_extension.md): Details on the A2UI Extension spec.
*   [v0.9.1 Basic Catalog Implementation](references/spec_v0.9.1_basic_catalog.md): Standard catalog implementation guide.
*   [v0.9.1 Evolution Guide](references/spec_v0.9.1_evolution.md): Migrating from earlier versions.
*   **JSON Schemas**:
    *   [Client Data Model](references/schema_v0.9.1_client_data_model.json)
    *   [Basic Catalog](references/schema_v0.9.1_catalog.json)
    *   [Common Types](references/schema_v0.9_common_types.json)

### 6. Ecosystem & Other
*   [Open Source Examples](references/open_source_examples.md): Links to official samples, community renderers, and open-source integrations.
*   [Community Renderers](references/ecosystem_renderers.md)
*   [Community Projects](references/ecosystem_community.md)
*   [A2UI in the World](references/ecosystem_in_the_world.md)
*   [A2UI Composer](references/composer.md)
*   [Roadmap](references/roadmap.md)

## Workflow
1.  **Identify the User's Goal:** What exactly are they trying to do? Are they learning concepts, building an agent, integrating a client, authoring components, or looking up spec details?
2.  **Read the Relevant Reference:** Immediately read the matching file(s) in the `references/` directory.
3.  **Provide Code or Answers:** Use the code samples and exact JSON structures defined in the documentation to fulfill the request. If generating code, make sure to strictly adhere to the models and SDK references.
