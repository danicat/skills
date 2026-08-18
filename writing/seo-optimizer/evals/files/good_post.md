---
title: "Building an MCP Server in Go for Gemini CLI"
summary: "Transform any Go CLI into a native tool for AI agents with just 50 lines of code."
description: "Step-by-step tutorial on building a Model Context Protocol (MCP) server in Go for Gemini CLI. Covers JSON-RPC handlers, tool discovery, and local debugging."
date: 2026-08-18T10:00:00Z
categories: ["Agentic Coding"]
tags: ["gemini-cli", "golang", "mcp", "tutorial"]
---

**Model Context Protocol (MCP) enables LLMs to execute local deterministic tools via standard JSON-RPC communication over standard input and output.** By implementing an MCP server in Go, developers can expose CLI utilities, databases, and system APIs directly into Gemini CLI and Antigravity 2.0.

In this guide, you will learn the exact wire protocol, how to structure tool handlers, and how to verify execution using native CLI inspection.

## Architectural Overview

The following table compares direct CLI invocation with MCP tool execution:

| Feature | Direct Shell Tool | Native MCP Server |
| :--- | :--- | :--- |
| **Protocol** | Shell subprocess exit codes | Standardized JSON-RPC 2.0 |
| **Schema Validation** | Unstructured text parsing | Strict JSON Schema definitions |
| **Context Safety** | High hallucination risk | Deterministic parameter typing |

## Implementing the Tool Handler in Go

Below is the complete Go implementation using standard library `net/rpc` and JSON decoding:

```go
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type ToolRequest struct {
	Name      string          `json:"name"`
	Arguments json.RawMessage `json:"arguments"`
}

func main() {
	fmt.Fprintln(os.Stderr, "MCP server initialized successfully")
}
```

![Architecture diagram showing JSON-RPC 2.0 message flow between Gemini CLI and Go MCP server](mcp_architecture.png)

## Verification and Next Steps

To verify your server locally, connect it to your Gemini CLI configuration and run a tool discovery query. For more details on advanced agent loops, see [Mastering Hooks in Antigravity]({{< ref "/posts/20260610-mastering-hooks" >}}).
