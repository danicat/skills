---
name: a2ui_developer_guide
description: A comprehensive developer guide and knowledge base for the A2UI (Agent-Driven User Interfaces) protocol. Use this skill when asked to write code for A2UI agents (Python, ADK), clients, frontend libraries, renderers, or when asked questions about the A2UI v0.9.1 specification.
---

# A2UI Developer Guide

This skill serves as the ultimate reference for developing applications, agents, and client libraries using the **A2UI (Agent-Driven User Interfaces) Protocol**, specifically focusing on the **v0.9.1 specification**. 

A2UI is a streaming protocol designed to allow Agents to emit rich, interactive UI components directly into the chat stream.

## Core Mandates
When working with A2UI, you MUST consult the reference documentation provided in the `references/` directory. Do not guess the structure of the JSON payload, the client data models, or the expected component formats. Always verify against the spec.

## Reference Material
All references have been crawled directly from the official [A2UI.org](https://a2ui.org) documentation and converted to markdown. They are located in the `references/` directory of this skill. 

Use the `view_file` tool to read the contents of the relevant reference file before responding:

1.  **Specification & Protocol:**
    *   [Catalogs Concept](references/catalogs_concept.md): General concepts on what a Catalog is and how it works.
    *   [v0.9.1 Core Specification](references/spec_v0.9.1.md): The absolute source of truth for the A2UI v0.9.1 data models, JSON schemas, component states, and messaging.
    *   [v0.9.1 Extension Specification](references/extension_spec_v0.9.1.md): Details on the A2UI Extension spec.
    *   [v0.9.1 Basic Catalog Implementation](references/basic_catalog_v0.9.1.md): Standard catalog implementation guide.
    *   [Basic Catalog JSON Schema](references/basic_catalog_schema.json): The raw JSON schema for the Basic Catalog.

2.  **Implementation Guides (Code Samples included):**
    *   [Quickstart](references/quickstart.md): Contains the fastest path to getting a basic A2UI application running.
    *   [Agent Development](references/agent_development.md): Learn how to build Agents that emit A2UI components using Python and ADK (Agent Development Kit).
    *   [Client Setup](references/client_setup.md): Guide on how to consume the A2UI protocol on the frontend (React, Next.js, etc).
    *   [Renderer Development](references/renderer_development.md): How to build custom renderers for interpreting A2UI components on the client.
    *   [Authoring Components](references/authoring_components.md): How to create new interactive UI components for agents to use.
    *   [Defining Your Own Catalog](references/defining_your_own_catalog.md): How to build custom catalogs that directly map to your existing component library.
    *   [A2UI in MCP Apps](references/a2ui_in_mcp_apps.md): Using the Model Context Protocol (MCP) in conjunction with A2UI.

## Workflow
1.  **Identify the User's Goal:** Are they building an Agent (Python/ADK), setting up a Client (React/Frontend), building a Renderer, or asking about the Spec?
2.  **Read the Relevant Reference:** Immediately read the matching file in the `references/` directory.
3.  **Provide Code or Answers:** Use the code samples and exact JSON structures defined in the documentation to fulfill the request. If generating code, make sure to strictly adhere to the v0.9.1 models.
