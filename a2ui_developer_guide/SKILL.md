---
name: a2ui_developer_guide
description: A comprehensive developer guide for A2UI v0.9.1. Trigger this skill for ANY question, bug, or coding task related to Agent-Driven User Interfaces (A2UI), MCP integrations, or component authoring.
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
---

# A2UI Developer Guide

This skill provides the reference for building applications, agents, and client libraries with the **A2UI (Agent-Driven User Interfaces) Protocol**. 

A2UI is a streaming protocol that lets agents emit interactive UI components directly into a chat stream.

## Core Mandates
When using A2UI, consult the reference documentation in the `references/` directory. Do not guess the structure of the JSON payload, client data models, or component formats. Always verify against the specification.

## Reference Material
All references are taken from the official [A2UI.org](https://a2ui.org) documentation. They are located in the `references/` directory. 

Use the `view_file` tool to read the contents of the relevant reference file before responding:

### 1. Introduction
*   [What is A2UI?](references/intro_what_is_a2ui.md)
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
*   [MCP Integration Guides](references/guide_mcp_integration.md): Integrating A2UI with the Model Context Protocol.

### 4. SDKs and Reference
*   [Messages](references/ref_messages.md): Full reference of valid A2UI protocol messages.
*   [Components](references/ref_components.md): Standard components reference.
*   [SDK References](references/ref_sdks.md): Renderers SDK (React, Angular, Lit, Flutter) and Agents SDK (Python/ADK) references.

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

## Workflow
1.  **Identify the User's Goal:** What exactly are they trying to do? Are they learning concepts, building an agent, integrating a client, authoring components, or looking up spec details?
2.  **Read the Relevant Reference:** Immediately read the matching file(s) in the `references/` directory.
3.  **Provide Code or Answers:** Use the code samples and exact JSON structures defined in the documentation to fulfill the request. If generating code, make sure to strictly adhere to the models and SDK references.


## Progressive Reference Loading
Do not try to load all references at once. Load them progressively as needed to conserve context:
1. Start with `concept_overview.md` and the relevant guide.
2. Only load schemas and spec files when you need to write or validate precise payloads.

## Custom Gotchas
* **Use the SDKs**: Always use the proper A2UI SDKs (Renderers and Agents). DO NOT attempt to manually re-implement protocol serialization or deserialization.
* **Separation of Concerns**: Maintain a strict boundary between frontend client renderers and backend agents.
* **Transport Layers**: Understand the differences between MCP, A2A, and AGUI transports when establishing communication.

## Plan-Validate-Execute Structure
When modifying component trees or catalogs:
1. **Plan**: Outline the intended changes to the structure.
2. **Validate**: Check the proposed changes against `spec_v0.9.1_core.md` and relevant JSON schemas.
3. **Execute**: Apply the updates using the provided SDK methods.
