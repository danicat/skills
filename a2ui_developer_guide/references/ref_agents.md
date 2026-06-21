# ref_agents
Source: https://a2ui.org/reference/agents/

# Agents (Server-Side)[¶](#agents-server-side "Permanent link")

Agents are server-side programs that generate A2UI messages in response to user requests.

The actual component rendering is done by the [renderer](../renderers/),
after messages are [transported](../../concepts/transports/) to the client.
The agent is only responsible for generating the A2UI messages.

## How Agents Work[¶](#how-agents-work "Permanent link")

The agent workflow typically involves the following steps:

1. **Receive** user message.
2. **Process** with LLM (Gemini, GPT, Claude, etc.).
3. **Generate** A2UI JSON messages as structured output.
4. **Send** to client via transport.

User interactions from the client can be treated as new user input.

## Sample Agents[¶](#sample-agents "Permanent link")

The A2UI repository includes sample agents you can learn from:

* [Restaurant Finder](https://github.com/a2ui-project/a2ui/tree/main/samples/agent/adk/restaurant_finder)
  + Table reservations with forms.
  + Written with the ADK.
* [Rizzcharts](https://github.com/a2ui-project/a2ui/tree/main/samples/community/agent/adk/rizzcharts/python)
  + A2UI Custom components demo.
  + Written with the ADK.
* [Orchestrator](https://github.com/a2ui-project/a2ui/tree/main/samples/community/agent/adk/orchestrator)
  + Passes A2UI messages from remote subagents.
  + Written with the ADK.

## Agent Types in A2A[¶](#agent-types-in-a2a "Permanent link")

### 1. User Facing Agent (standalone)[¶](#1-user-facing-agent-standalone "Permanent link")

A user facing agent is one that is directly interacted with by the user.

### 2. User Facing Agent as a host for a Remote Agent[¶](#2-user-facing-agent-as-a-host-for-a-remote-agent "Permanent link")

This is a pattern where the user facing agent is a host for one or more remote agents. The user facing agent will call the remote agent and the remote agent will generate the A2UI messages. This is a common pattern in [A2A](https://a2a-protocol.org) with the client agent calling the server agent.

In this pattern, the user-facing agent can handle messages in two ways:

* The user facing agent may "passthrough" the A2UI message without altering them.
* The user facing agent may alter the A2UI message before sending it to the client.

### 3. Remote Agent[¶](#3-remote-agent "Permanent link")

A remote agent is not directly a part of the user facing UI. Instead it is registered in as a remote agent and can be called by the user facing agent. This is a common pattern in [A2A](https://a2a-protocol.org) with the client agent calling the server agent.