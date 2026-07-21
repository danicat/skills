# guide_a2ui_in_mcp_apps
Source: https://a2ui.org/guides/a2ui-in-mcp-apps/

# A2UI Dynamic Rendering within MCP Applications[¶](#a2ui-dynamic-rendering-within-mcp-applications "Permanent link")

This guide shows you how to serve rich, interactive A2UI interfaces within [MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview) using Tools and Embedded Resources. By the end, you'll have a working MCP server that returns an MCP App which can render A2UI components and handle A2UI interactions. By supporting native A2UI within MCP Apps, your MCP server can securely collaborate with remote agents while maintaining consistency over UI styling.

![Generative document editor demo — highlighting text and interacting with dynamic A2UI controls to generate and revise content](../../assets/editor.gif)

## Prerequisites[¶](#prerequisites "Permanent link")

* **[Python 3.10+](https://www.python.org/)**
* **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
* **[Node.js 18+](https://nodejs.org/)** (for the MCP Inspector)

## Quick Start: Run the Sample[¶](#quick-start-run-the-sample "Permanent link")

For detailed instructions on how to run this sample, please refer to the [README.md](https://github.com/a2ui-project/a2ui/blob/main/samples/community/mcp/a2ui-in-mcpapps/README.md).

## Architecture Overview[¶](#architecture-overview "Permanent link")

The system consists of three main actors interacting through a chain of communication:

1. **Client Host Application**: The outer container (e.g., an Angular app) that connects to the MCP Server and hosts the secure sandbox for the MCP App.
2. **MCP Application (Sandboxed)**: The untrusted third-party web application (e.g., a Lit or Angular micro-app) running inside a double-iframe sandbox. This app contains the A2UI surface.
3. **MCP Server**: The backend server providing the application resources and handling tool calls.

```
flowchart TD
    %% Style Definitions
    classDef client fill:#e8f0fe,stroke:#1a73e8,color:#185abc,stroke-width:2px
    classDef server fill:#f1f3f4,stroke:#3c4043,color:#202124,stroke-width:2px
    classDef agent fill:#eef3fc,stroke:#74a0f7,color:#185abc,stroke-width:2px

    %% 1. Top: AI Agent Environment
    subgraph AgentEnv ["Server-Side Environment"]
        direction LR
        Agent["Generative A2UI Agent (e.g., Smart Agent)"]:::agent
        MCPServer["MCP Server"]:::server
    end

    %% 3. Bottom: Client-Side Environment
    subgraph ClientEnv ["Client-Side Environment"]
        Host["Client Host Application"]:::client

        subgraph SandboxBound ["Double-IFrame Sandbox"]
            subgraph McpApp ["MCP App (e.g., Editor App)"]
                direction TB
                %% Added a dedicated node for the app logic to prevent child-to-parent layout collapse
                AppLogic["Web Native App<br/>(e.g., Editor Panel)"]:::client
                A2UISurface["A2UI Surface<br/>(e.g., Controls Panel)"]:::client
                AppBridge["App Bridge"]:::client
                A2UIRenderer["A2UI Rendering Engine"]:::client

            end

            %% Changed connection to target the node inside, not the subgraph wrapper
            AppBridge -->|"A2UI JSON"| A2UIRenderer
            A2UIRenderer -.->|"Mounts & renders dynamic controls inside"| A2UISurface
            A2UISurface -->|"User Action<br/>(e.g., Generate text)"| AppBridge
            AppLogic -->|"Context Trigger<br/>(e.g., Highlight text)"| AppBridge
            AppBridge -->|"Update (e.g., Revised text)"| AppLogic
            A2UISurface -->|"Update<br/>(e.g., Accept/Reject)"| AppLogic
        end

        Host <-->|"postMessage Bridge"| AppBridge
    end

    %% --- Strictly Vertical Stacking Connections ---
    Agent <==>|"Delegation & Payload"| MCPServer
    MCPServer <==>|"MCP Protocol"| Host

    %% --- Local Context Flow Indicators ---
    %% Updated links to point to AppLogic instead of the McpApp subgraph
```

## Deep Dive: The Communication Flow[¶](#deep-dive-the-communication-flow "Permanent link")

A key aspect of this pattern is that the **MCP App** renders the A2UI payloads directly, rather than relying on the Client Host Application to do so.

### Loading A2UI Components in MCP Apps[¶](#loading-a2ui-components-in-mcp-apps "Permanent link")

Here is the sequence of events for dynamically loading A2UI components into MCP Apps:

1. **Trigger**: The MCP App decides it needs to fetch or update UI content (e.g., on initialization or via a user-initiated Action).
2. **Request**: The MCP App sends a JSON-RPC request to the Host via `window.parent.postMessage`.
   * *Example Method*: `ui/fetch_counter_a2ui`
3. **Relay**: The Sandbox Proxy relays this message to the Client Host.
4. **MCP Call**: The Client Host translates this custom message into a standard MCP `tools/call` request to the MCP Server.
   * *Example Tool*: `fetch_counter_a2ui`
5. **Response**: The MCP Server executes the tool and returns a result containing an `application/a2ui+json` resource.
6. **Response forwarding**: The Host receives the tool result and forwards it back down through the Sandbox Proxy to the MCP App.
7. **Rendering**: The MCP App extracts the A2UI JSON payload from the resource and feeds it into its local A2UI `MessageProcessor`, which updates the A2UI surface dynamically.

### Handling User Actions[¶](#handling-user-actions "Permanent link")

Interactivity within the rendered A2UI surface is handled by reversing the flow:

1. A user clicks a button within the A2UI surface inside the MCP App.
2. The A2UI component triggers a `userAction`.
3. The MCP App captures this event via the A2UI `MessageProcessor.events` subscription.
4. The MCP App packages the action and sends it as a JSON-RPC message to the Host (e.g., `ui/increase_counter`).
5. The Host calls the corresponding tool on the MCP Server.
6. The Server returns a new A2UI payload (representing the updated state), which is piped back to the MCP App to update the rendering.

### Sequence Diagram[¶](#sequence-diagram "Permanent link")

```
sequenceDiagram
    participant Server as MCP Server
    participant Host as Client Host Application
    participant Proxy as Sandbox Proxy
    participant App as MCP App (Sandbox)
    participant A2UI as A2UI Surface

    rect rgb(240, 248, 255)
    Note right of Server: INITIALIZATION & LOADING
    Note over Host: 1. Loaded from Hosting server
    Host->>Server: 2. Fetch MCP App resource
    Server-->>Host: Return MCP App resource
    Host->>Proxy: 3a. Load Sandbox Proxy
    Proxy->>App: 3b. Serve App in isolated iframe
    Note over App: 4. User action triggers resource  request
    App->>Proxy: Request tool call
    Proxy->>Host: Relay Request
    Host->>Server: Forward Tool Call
    Server-->>Host: 5. Respond with A2UI JSON payload
    Host->>Proxy: Relay payload
    Proxy->>App: 6. Hand down payload to MCP App
    App->>A2UI: 7. Renders A2UI Components
    end

    rect rgb(255, 245, 238)
    Note right of Server: USER INTERACTION
    Note over A2UI: Click on A2UI Button
    A2UI->>App: 8. A2UI Button triggers UserAction
    Note over App: 9. Translate A2UI UserAction to JSON-RPC message
    App->>Proxy: Forward JSON-RPC message
    Proxy->>Host: Relay JSON-RPC message
    Note over Host: 10. Map Action to Tool Call
    Host->>Server: Forward Tool Call
    Server-->>Host: 11. Respond with A2UI payload (datamodelupdate)
    Host->>Proxy: Relay payload
    Proxy->>App: 12. Pipe payload to MCP App
    App->>A2UI: Update rendering
    end
```

## How to Implement[¶](#how-to-implement "Permanent link")

To build your own MCP App with A2UI capabilities, follow these steps:

### Step 1: Inlining the Renderer[¶](#step-1-inlining-the-renderer "Permanent link")

MCP Apps are typically delivered as a single HTML resource from the MCP Server. To achieve this with a modern framework like Angular or React:

1. Build your application normally to produce static assets (`index.html`, `.js`, `.css`).
2. Use a post-build script (like the [`inline.js`](https://github.com/a2ui-project/a2ui/blob/main/samples/community/mcp/a2ui-in-mcpapps/server/apps/src/inline.js) script in the sample) to read the `index.html` and replace external `<script src="...">` and `<link rel="stylesheet" href="...">` tags with inline `<script>` and `<style>` tags containing the actual file contents.
3. This produces a self-contained HTML file that can be safely loaded via `srcdoc` in the restricted iframe.

Using Vite to inline

If your project uses Vite (common for React, Vue, or Lit), you can achieve the same single-file output automatically using plugins like `vite-plugin-singlefile`. This eliminates the need for a custom post-build script by handling the inlining during the build process itself.

**How to use it:**

1. **Install the plugin**:

   ```
   npm install -D vite-plugin-singlefile
   ```
2. **Configure Vite**: Add the plugin to your `vite.config.ts` (or `.js`):

   ```
   import {defineConfig} from 'vite';
   import {viteSingleFile} from 'vite-plugin-singlefile';

   export default defineConfig({
     plugins: [viteSingleFile()],
   });
   ```

   This will ensure that all JS and CSS assets are inlined into the `index.html` file on build, making it ready to be served by your MCP server as a single resource.

### Step 2: Leveraging A2UI-over-MCP[¶](#step-2-leveraging-a2ui-over-mcp "Permanent link")

Your inlined app is now running in the sandbox. To leverage A2UI:

1. **Include the A2UI Angular/Lit libraries** in your app's bundle.
2. **Define a communication contract** with your Host to interact with the MCP Server.
3. When you receive the response from the Host, look for the `application/a2ui+json` mimeType in the content.
4. Parse the JSON text and pass it to the A2UI [`MessageProcessor`](https://github.com/a2ui-project/a2ui/blob/main/renderers/angular/src/v0_8/data/processor.ts).

**Example: Fetching and Rendering A2UI**

```
// 1. Request A2UI data from Host
const result = await callHostMethod('ui/fetch_counter_a2ui');

// 2. Find and parse the A2UI resource
const a2uiResource = result.find(
  c => c.type === 'resource' && (c.resource?.mimeType === 'application/a2ui+json' || c.resource?.mimeType === 'application/json+a2ui'),
);

if (a2uiResource?.resource?.text) {
  const messages = JSON.parse(a2uiResource.resource.text);
  this.processor.processMessages(messages);
}

// Utility for JSON-RPC communication
function callHostMethod(method: string, params: any = {}): Promise<any> {
  return new Promise((resolve, reject) => {
    const requestId = `${method}-${Date.now()}`;

    const handler = (event: MessageEvent) => {
      if (event.data.id !== requestId) return;
      window.removeEventListener('message', handler);

      if (event.data.error) {
        reject(event.data.error);
      } else {
        resolve(event.data.result);
      }
    };

    window.addEventListener('message', handler);

    window.parent.postMessage(
      {
        jsonrpc: '2.0',
        id: requestId,
        method,
        params,
      },
      '*',
    ); // Note: Replace "*" with explicit target origin in production
  });
}
```

### Step 3: Handling User Actions on A2UI Components[¶](#step-3-handling-user-actions-on-a2ui-components "Permanent link")

To handle interactivity within the rendered A2UI surface, your MCP App must capture A2UI events and forward them to the Host using JSON-RPC.

**Example: Handling User Actions**

```
// Subscribing to A2UI events in the MCP App ([main.ts](https://github.com/a2ui-project/a2ui/blob/main/samples/community/mcp/a2ui-in-mcpapps/server/apps/src/src/main.ts))
this.processor.events.subscribe(async event => {
  if (!event.message.userAction) return;

  const method = `ui/${event.message.userAction.name}`;
  const params = event.message.userAction.context;

  try {
    // Translate A2UI UserAction to JSON-RPC, send to Host, and await response
    const result = await callHostMethod(method, params);

    // Parse the updated A2UI payload and update the rendering
    const messages = extractA2UIMessages(result);
    if (messages) {
      this.processor.processMessages(messages);
    }
  } catch (error) {
    console.error(`Error handling user action[${method}]:`, error);
  }
});
```

This pattern enables the MCP App to serve as a dynamic interface for the MCP Server's A2UI capabilities while maintaining strict security isolation.

### Inlined MCP App HTML Pseudocode[¶](#inlined-mcp-app-html-pseudocode "Permanent link")

To put this all together, here is an HTML mockup representing a compiled and inlined MCP Application. It defines the placeholder UI with a native `<a2ui-surface>` element, initializes the `AppBridge` to communicate with the outer host, fetches its dynamic A2UI layout on load, and processes events using the loaded A2UI SDK:

```
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Inlined MCP App Surface</title>
    <!-- Assumes the standard A2UI SDK script is bundled or loaded -->
  </head>
  <body>
    <div>
      <h3>MCP App (Editor Panel)</h3>
      <p>This text is native to the sandboxed third-party app.</p>

      <!-- A2UI Surface custom element provided by the A2UI SDK -->
      <a2ui-surface surfaceId="recipe-card"></a2ui-surface>
    </div>

    <script>
      // Note: The pseudocode below assumes AppBridge from @modelcontextprotocol/ext-apps
      // and a2uiProcessor from the A2UI SDK are preloaded or inlined.
      const bridge = new AppBridge({name: 'editor-panel', version: '1.0.0'});

      // Helper to extract and process dynamic A2UI responses from tool results
      function processA2UIResponse(result) {
        const a2uiResource = result?.content?.find(
          c => c.type === 'resource' && (c.resource?.mimeType === 'application/a2ui+json' || c.resource?.mimeType === 'application/json+a2ui'),
        );
        if (a2uiResource?.resource?.text) {
          const payload = JSON.parse(a2uiResource.resource.text);
          window.a2uiProcessor.processMessages(payload);
        }
      }

      // 1. Initialize AppBridge and fetch initial controls
      async function initApp() {
        await bridge.connect();

        // Call server tool to load initial layout controls
        const result = await bridge.callServerTool({name: 'fetch_controls', arguments: {}});
        processA2UIResponse(result);
      }

      // 2. Handle interactive User Actions routed by the A2UI SDK
      window.a2uiProcessor.events.subscribe(async event => {
        if (!event.message.userAction) return;
        const action = event.message.userAction;

        // Route the user action directly via the bridge to the MCP Server tool
        const result = await bridge.callServerTool({
          name: action.name,
          arguments: action.context,
        });

        // Feed any updated server UI states back to the A2UI processor
        processA2UIResponse(result);
      });

      // Initialize the app on startup
      initApp();
    </script>
  </body>
</html>
```

## Security Considerations[¶](#security-considerations "Permanent link")

* **Explicit Target Origin**: Always use specific target origins (e.g., `'https://trusted-host.com'`) instead of `*` when calling `postMessage` if the host origin is known. This prevents malicious iframes from intercepting your RPC requests.
* **Null Origin Handling**: Remember that inside a strict sandbox (`sandbox="allow-scripts"` without `allow-same-origin`), `window.location.origin` will evaluate to `"null"`. You must validate incoming messages carefully by comparing `event.source` against the expected window object (e.g., `window.parent`).# guide_a2ui_over_mcp
Source: https://a2ui.org/guides/a2ui_over_mcp/

# A2UI over Model Context Protocol (MCP)[¶](#a2ui-over-model-context-protocol-mcp "Permanent link")

This guide shows you how to serve **rich, interactive A2UI interfaces** from an **MCP server** using Tools and Embedded Resources. By the end, you'll have a working MCP server that returns A2UI components to any MCP-compatible client.

[

Your browser does not support the video tag.
](https://raw.githubusercontent.com/a2ui-project/a2ui/main/docs/assets/guides-a2ui-over-mcp-tour.mp4)

## Prerequisites[¶](#prerequisites "Permanent link")

Ensure you have the following installed before you begin:

* **Python** (version 3.10 or later).
* **[uv](https://docs.astral.sh/uv/)** for fast Python package management.
* **Node.js** (version 18 or later) for the MCP Inspector.

## Quick Start: Run the Sample[¶](#quick-start-run-the-sample "Permanent link")

Before diving into the protocol details, let's get a working example running. The A2UI repo includes a ready-to-go MCP recipe demo.

```
# Clone the repo (if you haven't already)
git clone https://github.com/a2ui-project/a2ui.git
cd a2ui/samples/mcp/a2ui-over-mcp-recipe

# Start the MCP server (SSE transport on port 8000)
uv run .
```

### Option A: Interacting via the MCP Inspector[¶](#option-a-interacting-via-the-mcp-inspector "Permanent link")

In a separate terminal, launch the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to interact with the server:

```
npx @modelcontextprotocol/inspector
```

In the Inspector:

1. Set **Transport Type** to `SSE`
2. Connect to `http://localhost:8000/sse`
3. Click **List Resources** → you'll see "Recipe Form" resource.
4. Read the `a2ui://recipe-form` resource → the resource content is the A2UI JSON that renders the simple form.
5. Click **List Tools** → you'll see `get_recipe_a2ui`
6. Run the tool → the response contains A2UI JSON that renders a recipe card

> NOTE: Note
>
> The sample uses a local path reference to the A2UI Agent SDK. For your own projects, install from PyPI:
>
> ```
> pip install a2ui-agent-sdk
> ```

### Option B: Running the Recipe Client Web App[¶](#option-b-running-the-recipe-client-web-app "Permanent link")

For a fully rendered interactive experience that visually demonstrates A2UI over MCP, run the included web application:

**Package Manager Usage:** Running the built-in sample applications within the A2UI repository requires Yarn (`yarn install` / `yarn dev`) as configured by Corepack workspaces. For your own regular usage and standalone projects outside this repository, use the package manager of your choice (e.g. npm, pnpm).

1. In a new terminal window, navigate to the client directory:

   ```
   cd client
   ```
2. Install Node.js dependencies:

   ```
   yarn install
   ```
3. Start the Vite development server:

   ```
   yarn dev
   ```
4. Open your browser to the URL displayed in your terminal (usually `http://localhost:5173`).

You will see a premium, responsive dual-column interface where the left column renders the Selection Form from MCP Resource (`a2ui://recipe-form`). Picking options and clicking **"Get Recipe"** executes the MCP Tool (`get_recipe_a2ui`), dynamically rendering the returned custom A2UI recipe card in the right column.

![Dynamic Recipe Studio demo showing selection form on the left and dynamic recipe card generation on the right](../../assets/recipe_sample.gif)

See all samples at [`samples/community/mcp/`](https://github.com/a2ui-project/a2ui/tree/main/samples/community/mcp).

## How It Works[¶](#how-it-works "Permanent link")

There are two primary ways an MCP server can deliver A2UI content to a client:

1. **Via Reading a Resource (`resources/read`)**: The client reads an MCP resource directly (e.g., `a2ui://recipe-form`). The server returns the A2UI JSON payload directly.
2. **Via Calling a Tool (`tools/call`)**: The client calls an MCP tool (e.g., `get_recipe_a2ui`). The server returns the A2UI JSON payload wrapped as an **Embedded Resource** inside the tool response.

In both cases, the client detects the `application/a2ui+json` MIME type and routes the payload to an A2UI renderer.

MIME Type Uniformity

Regardless of the delivery channel (whether fetched directly as a Resource or returned inside a Tool's `CallToolResult`), the A2UI JSON payload is always identified by the `application/a2ui+json` MIME type. In Tool responses, the payload must be wrapped inside an `EmbeddedResource` carrying this MIME type. This uniform identification allows client-side middleware to seamlessly intercept and route both static resources and dynamic tool responses to A2UI.

### 1. Resource-based Delivery Flow (`resources/read`)[¶](#1-resource-based-delivery-flow-resourcesread "Permanent link")

```
Client → resources/read → MCP Server
                             ↓
                 Retrieve A2UI JSON
                             ↓
Client ← ResourceContents ← MCP Server
          (application/a2ui+json)
   ↓
A2UI Renderer displays UI
```

### 2. Tool-based Delivery Flow (`tools/call`)[¶](#2-tool-based-delivery-flow-toolscall "Permanent link")

```
Client → tools/call → MCP Server
                         ↓
              Generate A2UI JSON
                         ↓
         Wrap as EmbeddedResource
              (application/a2ui+json)
                         ↓
Client ← CallToolResult ← MCP Server
   ↓
A2UI Renderer displays UI
```

## Resources vs. Tools: Separation of Utility Focus[¶](#resources-vs-tools-separation-of-utility-focus "Permanent link")

When designing an A2UI integration over MCP, you should choose between **Resources** and **Tools** depending on whether the UI payload is static or dynamic.

### 1. Static UI via MCP Resources (`resources/read`)[¶](#1-static-ui-via-mcp-resources-resourcesread "Permanent link")

For simple, static user interfaces that do not depend on user prompt inputs or conversation history, you should serve A2UI directly as an MCP Resource.

* **Concept**: The client reads a pre-defined A2UI resource using a standard resource URI (e.g., `a2ui://recipe-form`).
* **Use Case**: Ideal for static configuration forms, selection screens, settings dashboards, or stable layouts.
* **Benefit**: Extremely simple to implement, low overhead, and doesn't require the LLM/Agent to make a tool call to fetch the structure.

**Python Server Example:**

```
@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="a2ui://recipe-form",
            name="Recipe Form",
            mimeType="application/a2ui+json",
            description="Static form allowing users to pick options.",
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> list[ReadResourceContents]:
    if uri == "a2ui://recipe-form":
        return [
            ReadResourceContents(
                content=json.dumps(recipe_form_json),
                mime_type="application/a2ui+json",
            )
        ]
    raise ValueError(f"Unknown resource: {uri}")
```

### 2. Dynamic UI via MCP Tools (`tools/call`)[¶](#2-dynamic-ui-via-mcp-tools-toolscall "Permanent link")

For user interfaces that need to be generated dynamically based on the conversational context, user parameters, or real-time data, you should serve A2UI inside an MCP Tool's response.

* **Concept**: The client/Agent calls a tool with specific arguments (e.g., chosen ingredients, preferences), and the server returns a customized A2UI JSON wrapped inside an `EmbeddedResource` in the `CallToolResult`.
* **Use Case**: Ideal for content that depends on live database queries, previous inputs, interactive step-by-step wizard state, or personalized recommendations (e.g., a customized recipe card).
* **Benefit**: Maximizes flexibility, context-awareness, and supports highly dynamic flows.
* **Best Practice (Fallback Text)**: Always include a `TextContent` alongside your `EmbeddedResource` in the `CallToolResult`. Clients that don't support A2UI will fall back to displaying this text to the user.

**Python Server Example:**

```
@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> types.CallToolResult:
    if name == "get_recipe_a2ui":
        # Resolve dynamic selections from client parameters
        style = arguments.get("cookingStyle", "Baked")
        protein = arguments.get("protein", "Salmon")

        # Retrieve customized recipe database entry
        recipe_data = RECIPES.get((style, protein))

        # Customize base A2UI schema dynamically
        custom_recipe_json = copy.deepcopy(recipe_a2ui_json)
        custom_recipe_json[1]["updateComponents"]["components"][0]["text"] = recipe_data["title"]

        # Return customized recipe card as EmbeddedResource
        return types.CallToolResult(content=[
            types.EmbeddedResource(
                type="resource",
                resource=types.TextResourceContents(
                    uri="a2ui://recipe-card",
                    mimeType="application/a2ui+json",
                    text=json.dumps(custom_recipe_json),
                )
            )
        ])
```

## Catalog Negotiation[¶](#catalog-negotiation "Permanent link")

Before a server can send A2UI to a client, they must establish which catalogs are available. Depending on your architecture, this can happen in one of two ways.

### Option A: During MCP Initialization (Recommended)[¶](#option-a-during-mcp-initialization-recommended "Permanent link")

MCP is a stateful session protocol, so the most efficient approach is to declare capabilities once during connection setup. The client declares its A2UI support under `capabilities`:

```
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "id": "init-123",
  "params": {
    "protocolVersion": "2025-11-25",
    "clientInfo": {
      "name": "a2ui-enabled-client",
      "version": "1.0.0"
    },
    "capabilities": {
      "a2ui": {
        "clientCapabilities": {
          "v0.9": {
            "supportedCatalogIds": [
              "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json"
            ]
          }
        }
      }
    }
  }
}
```

The server stores this state for the duration of the session.

### Option B: Per-Message Metadata (For Stateless Servers)[¶](#option-b-per-message-metadata-for-stateless-servers "Permanent link")

If your server must remain stateless, the client can pass A2UI capabilities in the `_meta` field of every tool call:

```
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": "id-123",
  "params": {
    "name": "generate_report",
    "arguments": {"date": "2026-03-01"},
    "_meta": {
      "a2ui": {
        "clientCapabilities": {
          "v0.9": {
            "supportedCatalogIds": [
              "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json"
            ],
            "inlineCatalogs": []
          }
        }
      }
    }
  }
}
```

## Handling User Actions[¶](#handling-user-actions "Permanent link")

Interactive components like `Button` can trigger actions that are sent back to the server as MCP tool calls.

### 1. Define a Button with an Action[¶](#1-define-a-button-with-an-action "Permanent link")

In your A2UI JSON, add an `action` to a component:

```
{
  "id": "confirm-button",
  "component": {
    "Button": {
      "child": "confirm-button-text",
      "action": {
        "event": {
          "name": "confirm_booking",
          "context": {
            "start": "/dates/start",
            "end": "/dates/end"
          }
        }
      }
    }
  }
}
```

### 2. Client Sends the Action as a Tool Call[¶](#2-client-sends-the-action-as-a-tool-call "Permanent link")

When the user clicks the button, the client resolves data bindings (like `/dates/start`) against the surface state and sends a tool call:

```
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": "id-456",
  "params": {
    "name": "action",
    "arguments": {
      "name": "confirm_booking",
      "context": {
        "start": "2026-03-20",
        "end": "2026-03-25"
      }
    }
  }
}
```

### 3. Handle the Action on the Server[¶](#3-handle-the-action-on-the-server "Permanent link")

```
@self.tool()
async def action(name: str, context: dict) -> types.CallToolResult:
    """Handle A2UI user actions."""
    if name == "confirm_booking":
        # Process the booking, then return confirmation UI
        return types.CallToolResult(content=[
            types.TextContent(
                type="text",
                text=f"Booking confirmed: {context['start']} to {context['end']}"
            )
        ])
    raise ValueError(f"Unknown action: {name}")
```

## Error Handling[¶](#error-handling "Permanent link")

Clients can report A2UI rendering errors back to the server via a tool call:

```
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": "id-789",
  "params": {
    "name": "error",
    "arguments": {
      "code": "INVALID_JSON",
      "message": "Failed to parse A2UI payload.",
      "surfaceId": "default"
    }
  }
}
```

Handle it on the server:

```
@self.tool()
async def error(code: str, message: str, surfaceId: str = "") -> types.CallToolResult:
    """Handle A2UI client errors."""
    # Log the error, retry, or send a fallback UI
    return types.CallToolResult(content=[
        types.TextContent(
            type="text",
            text=f"Acknowledged error {code}: {message}"
        )
    ])
```

## Verbalization and Visibility Control[¶](#verbalization-and-visibility-control "Permanent link")

Control whether the LLM can "read" A2UI payloads in subsequent turns using MCP **Resource Annotations**:

```
a2ui_resource = types.EmbeddedResource(
    type="resource",
    resource=types.TextResourceContents(
        uri="a2ui://training-plan-page",
        mimeType="application/a2ui+json",
        text=json.dumps(a2ui_payload)
    ),
    # Show the UI to the user, but hide the raw JSON from the LLM
    annotations=types.Annotations(audience=["user"])
)
```

| Audience | Behavior |
| --- | --- |
| *(empty)* | Visible to both user and LLM |
| `["user"]` | Rendered for the user; hidden from LLM context |
| `["assistant"]` | Available to LLM for follow-up reasoning; not rendered |

## Using the A2UI Agent SDK[¶](#using-the-a2ui-agent-sdk "Permanent link")

For production use, the **A2UI Agent SDK** handles schema management, validation, and prompt generation for you:

```
pip install a2ui-agent-sdk
```

```
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

# Initialize the schema manager with the basic catalog
schema_manager = A2uiSchemaManager(
    catalogs=[BasicCatalog.get_config()],
)

# Validate A2UI output before sending
selected_catalog = schema_manager.get_selected_catalog()
selected_catalog.validator.validate(a2ui_payload)
```

See the full [Agent Development Guide](../agent-development/) for details on schema management, dynamic catalogs, and streaming.

## Next Steps[¶](#next-steps "Permanent link")

* [A2UI Specification](../../specification/v0.9-a2ui/) — full protocol reference
* [Component Gallery](../../reference/components/) — browse available components
* [MCP Apps in A2UI Surface](../mcp-apps-in-a2ui/) — embed HTML-based MCP apps inside A2UI
* [Client Setup](../client-setup/) — build a renderer that displays A2UI# guide_mcp_apps_in_a2ui
Source: https://a2ui.org/guides/mcp-apps-in-a2ui/

# MCP Apps Integration in A2UI Surfaces[¶](#mcp-apps-integration-in-a2ui-surfaces "Permanent link")

This guide explains how **Model Context Protocol (MCP) Applications** are integrated and displayed within the **A2UI** surface, along with the security model and testing guidelines.

> NOTE: Looking for the core A2UI-over-MCP protocol? See [A2UI over MCP](../a2ui_over_mcp/) for how to return A2UI JSON payloads from MCP tool calls.

## Overview[¶](#overview "Permanent link")

The Model Context Protocol (MCP) allows MCP servers to deliver rich, interactive HTML-based user interfaces to hosts. A2UI provides a secure environment to run these third-party applications.

![MCP Calculator demo — loading the app, opening the calculator, and chatting with the agent](../../assets/mcp-apps-calculator-demo.gif)

## Double-Iframe Isolation Pattern[¶](#double-iframe-isolation-pattern "Permanent link")

To run untrusted third-party code securely, A2UI utilizes a **double-iframe** isolation pattern. This approach isolates raw DOM injection from the main application while maintaining a structured JSON-RPC channel.

### Security Rationale[¶](#security-rationale "Permanent link")

Standard single-iframe sandboxing with `allow-scripts` is often bypassed if combined with `allow-same-origin`, which defeats the containerization. Any iframe with `allow-scripts` and `allow-same-origin` can escape its sandbox by programmatically interacting with its parent DOM or removing its own sandbox attribute.

To prevent this, A2UI strictly excludes `allow-same-origin` for the inner iframe where the third-party application runs.

### The Architecture[¶](#the-architecture "Permanent link")

1. **[Sandbox Proxy (`sandbox.html`)](https://github.com/a2ui-project/a2ui/blob/main/samples/client/shared/mcp_apps_inner_iframe/sandbox.html)**: An intermediate `iframe` served from the same origin. It isolates raw DOM injection from the main app while maintaining a structured JSON-RPC channel.
   * Permissions: **Do not sandbox** in the host template (e.g., [`mcp-app.ts`](https://github.com/a2ui-project/a2ui/blob/main/samples/community/client/lit/mcp-apps-in-a2ui-sample/mcp-app.ts) or [`mcp-apps-component.ts`](https://github.com/a2ui-project/a2ui/blob/main/samples/community/client/lit/mcp-apps-in-a2ui-sample/ui/custom-components/mcp-apps-component.ts)).
   * Host origin validation: Validates that messages come from the expected host origin.
2. **Embedded App (Inner Iframe)**: The innermost `iframe`. Injected dynamically via `srcdoc` with restricted permissions.
   * Permissions: `sandbox="allow-scripts allow-forms allow-popups allow-modals"` (**MUST NOT** include `allow-same-origin`).
   * Isolation: Removes access to `localStorage`, `sessionStorage`, `IndexedDB`, and cookies due to unique origin.

### Physical Iframe Nesting[¶](#physical-iframe-nesting "Permanent link")

```
flowchart TD
    subgraph "Host Application"
        A[A2UI Page] --> B["Host Component e.g., McpApp"]
    end
    subgraph "Sandbox Proxy"
        B -->|Message Relay| C[iframe sandbox.html]
    end
    subgraph "Embedded App"
        C -->|Dynamic Injection| D[inner iframe untrusted content]
    end
```

### End-to-End Architecture & Lifecycle Flow[¶](#end-to-end-architecture-lifecycle-flow "Permanent link")

The complete cycle—including layout tree hierarchy, completely separated backend actors (the Proxy Agent and the MCP Server), and how isolated third-party widgets interact reactively with their native siblings (e.g., the Pong game's scoreboard)—is detailed below:

```
graph TD
    %% 1. Top Tier (Strict vertical hierarchy)
    MCPServer["MCP App Server<br/>(Hosts widget resources & core tools)"]

    %% 2. Middle-Top Tier
    Agent["AI Agent<br/>(A2UI Backend Coordinator)"]

    %% 3. Subgraph for Host layout tree (Bottom Tier)
    subgraph HostApp ["Host Application"]
        direction TB
        Shell["A2UI Rendering Engine & State Manager<br/>(Orchestrates native layout & state bindings)"]

        subgraph LayoutTree ["A2UI Component Tree"]
            McpComponent["McpApp Component<br/>(Sandboxed HTML/JS Widget)"]
            SiblingComponent["Other A2UI Components<br/>(e.g., PongScoreBoard)"]
        end

        Shell <-->|"1. Initialize postMessage Event Bridge"| McpComponent
        Shell -.->|"5. Reactive State Update<br/>(e.g., Render updated score)"| SiblingComponent
    end

    %% Vertical Channel connecting Top to Middle-Top
    MCPServer ==>|"MCP Protocol (SSE / Stdio)"| Agent

    %% Unidirectional Data Cycle (Flowing vertically through the center)
    McpComponent ==>|"2. Tool Action Request<br/>(e.g., score_update)"| Shell
    Shell ==>|"3. Action Delegation (A2UI Protocol)"| Agent
    Agent ==>|"4. State Mutation & Sync (dataModelUpdate)"| Shell

    %% Style Sibling Relationship
    McpComponent -.->|"No Direct Access (Strictly Isolated)"| SiblingComponent
```

#### How the Sibling Update Loop Works:[¶](#how-the-sibling-update-loop-works "Permanent link")

1. **Initialize postMessage Event Bridge (1)**: The host shell instantiates the double-iframe sandbox and establishes a secure message relay bridge with the `McpApp` component.
2. **Tool Action Request (2)**: When a user interacts with the sandboxed app (e.g., scores a point in the Pong game), the app triggers a tool action by posting a message over the postMessage bridge.
3. **Action Delegation (3)**: The host layout engine intercepts the action and delegates its execution to the `AI Proxy Agent` over the A2UI/A2A protocol. The agent optionally coordinates with the `MCP App Server` using the standard MCP Protocol (SSE / Stdio) if external calculation or resources are required.
4. **State Mutation & Sync (4)**: The agent processes the action, mutates the master session state, and pushes a `dataModelUpdate` back to the host state manager.
5. **Reactive State Update (5)**: The host updates its local store, triggering a reactive update on sibling A2UI components (such as native scoreboards or displays) bound to that state path. Direct communication between the sandboxed component and native sibling elements is strictly blocked to maintain containerization security.

## Usage / Code Example[¶](#usage-code-example "Permanent link")

The MCP Apps component typically resolves to a `custom` node in the A2UI catalog. Here is how a developer might use it in their code.

### 1. Register within the Catalog[¶](#1-register-within-the-catalog "Permanent link")

You must register the component in your catalog application. For example, in Angular:

```
import {Catalog} from '@a2ui/angular';
import {inputBinding} from '@angular/core';

export const DEMO_CATALOG = {
  McpApp: {
    type: () => import('./mcp-app').then(r => r.McpApp),
    bindings: ({properties}) => [
      inputBinding(
        'content',
        () => ('content' in properties && properties['content']) || undefined,
      ),
      inputBinding('title', () => ('title' in properties && properties['title']) || undefined),
    ],
  },
} as Catalog;
```

### 2. Usage in A2UI Message[¶](#2-usage-in-a2ui-message "Permanent link")

In the Host or Agent context, send an A2UI message that translates to this custom node.

```
{
  "type": "custom",
  "name": "McpApp",
  "properties": {
    "content": "<h1>Hello, World!</h1>",
    "title": "My MCP App"
  }
}
```

If the content is complex or requires encoding, you can pass a URL-encoded string:

```
{
  "type": "custom",
  "name": "McpApp",
  "properties": {
    "content": "url_encoded:%3Ch1%3EHello%2C%20World!%3C%2Fh1%3E",
    "title": "My MCP App"
  }
}
```

## Communication Protocol[¶](#communication-protocol "Permanent link")

Communication between the Host and the embedded inner iframe is facilitated via a structured JSON-RPC channel over `postMessage`.

* **Events**: The Host Component listens for a `SANDBOX_PROXY_READY_METHOD` message from the proxy.
* **Bridging**: An `AppBridge` handles message relaying. Developers (specifically the MCP App Developer inside the untrusted iframe) can call tools on the MCP server using `bridge.callTool()`.
* **The Host**: Resolves callbacks (e.g., specific resizing, Tool results).

### Limitations[¶](#limitations "Permanent link")

Because `allow-same-origin` is strictly omitted for the innermost iframe, the following conditions apply:

* The MCP app **cannot** use `localStorage`, `sessionStorage`, `IndexedDB`, or cookies. Each application runs with a unique origin.
* Direct DOM manipulation by the parent is blocked. All interactions must proceed via message passing.

## Prerequisites[¶](#prerequisites "Permanent link")

To run the samples, ensure you have the following installed:

* **Python 3.10+** — Required for the agent and MCP server backends
* **[uv](https://docs.astral.sh/uv/)** — Fast Python package manager (used to run all Python samples)
* **Node.js 18+** and **Yarn** — Required for building and running the sample client apps within this monorepo workspace.
* **A `GEMINI_API_KEY`** — Required by all ADK-based agents. Get one from [Google AI Studio](https://aistudio.google.com/apikey)

**Package Manager Usage:** Running the built-in sample applications within the A2UI repository requires Yarn as configured by Corepack workspaces. For your own regular usage and standalone projects outside this repository, use the package manager of your choice (e.g. npm, pnpm).

> ⚠️ **Environment variable setup**: You can either export `GEMINI_API_KEY` in your shell or create a `.env` file in each agent directory. The agents use `dotenv` to load `.env` files automatically.
>
> ```
> # Option 1: Export in shell
> export GEMINI_API_KEY="your-api-key-here"
>
> # Option 2: Create .env file in the agent directory
> echo 'GEMINI_API_KEY=your-api-key-here' > .env
> ```

## Samples[¶](#samples "Permanent link")

There are two primary samples demonstrating MCP Apps integration. Each sample requires running **multiple terminals** — one for each backend service and one for the client.

---

### Sample 1: MCP App Standalone Sample (Lit Client & ADK Agent)[¶](#sample-1-mcp-app-standalone-sample-lit-client-adk-agent "Permanent link")

This sample verifies the sandbox with a Lit-based client and an ADK-based A2A agent.

#### Step 1: Start the Agent[¶](#step-1-start-the-agent "Permanent link")

In a separate terminal, navigate to the agent directory and start the agent:

```
cd samples/agent/adk/mcp-apps-in-a2ui-sample
uv run agent.py
```

The agent will run on `http://localhost:8000`.

#### Step 2: Start the Client[¶](#step-2-start-the-client "Permanent link")

In a new terminal, navigate to the client directory and start the dev server (requires building the Lit renderer first):

```
cd samples/client/lit/mcp-apps-in-a2ui-sample
yarn install
yarn dev
```

The client starts at `http://localhost:5173/`.

#### Step 3: Open in Browser[¶](#step-3-open-in-browser "Permanent link")

Open your browser and navigate to `http://localhost:5173/`. You should see the A2UI interface loading the MCP App.

**What to expect**: A page loading the MCP App in a sandboxed iframe. Clicking the "Call Agent Tool" button inside the iframe will trigger an action that is handled by the agent.

---

### Sample 2: MCP Apps (Calculator + Pong) (Angular Client + MCP Server + Proxy Agent)[¶](#sample-2-mcp-apps-calculator-pong-angular-client-mcp-server-proxy-agent "Permanent link")

This sample verifies the sandbox with an Angular-based client, an MCP Proxy Agent, and a remote MCP Server. It requires **three** backend processes.

#### Step 1: Start the MCP Server (Calculator)[¶](#step-1-start-the-mcp-server-calculator "Permanent link")

```
cd samples/mcp/mcp-apps-calculator/
uv run .
```

The MCP server starts on `http://localhost:8000` using SSE transport.

#### Step 2: Start the MCP Apps Proxy Agent[¶](#step-2-start-the-mcp-apps-proxy-agent "Permanent link")

In a **new terminal**:

```
cd samples/agent/adk/mcp_app_proxy/
export GEMINI_API_KEY="your-key"  # or use a .env file
uv run .
```

The proxy agent starts on `http://localhost:10006` by default.

#### Step 3: Build and Start the Angular Client[¶](#step-3-build-and-start-the-angular-client "Permanent link")

In a **new terminal**:

```
cd samples/client/angular/

# Build the renderers (required — Angular depends on local renderer packages)
yarn build:renderer

yarn install
yarn build:sandbox
yarn start -- mcp_calculator
```

> ⚠️ **`build:renderer` and `build:sandbox` are both required**: `build:renderer` compiles the A2UI renderer packages that the Angular app depends on. `build:sandbox` bundles the sandbox proxy into the Angular project's public assets. Without either, the app won't work.

The client starts at `http://localhost:4200/`.

#### Step 4: Open in Browser[¶](#step-4-open-in-browser "Permanent link")

Navigate to:

```
http://localhost:4200/?disable_security_self_test=true
```

**What to expect**: A set of smart chips to load calculator app or pong app will be rendered. Both apps run in their own sandboxed iframes.

| Calculator App | Pong App |
| --- | --- |
| An animated GIF of the calculator app being used to perform multiplications. | An animated GIF of the pong app being played. |

---

## URL Options for Testing[¶](#url-options-for-testing "Permanent link")

For testing purposes, you can opt-out of the security self-test by using specific URL query parameters.

### `disable_security_self_test=true`[¶](#disable_security_self_testtrue "Permanent link")

This query parameter allows you to bypass the security self-test that verifies iframe isolation. This is useful for debugging and testing environments where the double-iframe setup may not pass strict origin checks (e.g., `localhost` development).

Example usage:

```
http://localhost:4200/?disable_security_self_test=true
```

## Troubleshooting[¶](#troubleshooting "Permanent link")

| Problem | Solution |
| --- | --- |
| `GEMINI_API_KEY environment variable not set` | Export the key or add a `.env` file in the agent directory |
| Python version error on `restaurant_finder` agent | Install Python 3.13+ (required by that sample's `pyproject.toml`) |
| `yarn build:renderer` fails | Make sure you ran `yarn install` first in `samples/client/lit/` |
| Angular client shows blank page | Ensure you ran `yarn build:sandbox` before `yarn start` |
| MCP app iframe doesn't load | Check that both the MCP server (port 8000) and proxy agent (port 10006) are running |
| `ng serve` not found | Run `yarn install` to install dev dependencies including `@angular/cli` |
| "URL with hostname not allowed" | Angular 21 restricts allowed hosts. Use `localhost` (the default) — do not pass `--host 0.0.0.0` |
| Security self-test fails in dev | Add `?disable_security_self_test=true` to the URL |