# Antigravity Hooks & Tool Integration Reference

Hooks intercept agent actions at specific lifecycle events in Antigravity. They are configured in `hooks.json` at the root of a plugin or in `.agents/hooks.json`.

---

## 1. `hooks.json` Schema

```json
{
  "hook-suite-name": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/safety-check.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "PostToolUse": [],
    "PreInvocation": [],
    "PostInvocation": [],
    "Stop": []
  }
}
```

---

## 2. Event Types & Matcher Rules

| Event | Description | Matcher Target |
| :--- | :--- | :--- |
| **`PreToolUse`** | Fires *before* a tool executes. | Tool name (regex pattern matching) |
| **`PostToolUse`** | Fires *after* a tool completes execution. | Tool name (regex pattern matching) |
| **`PreInvocation`** | Fires *before* calling the foundation model. | N/A (matcher ignored) |
| **`PostInvocation`** | Fires *after* model tool calls finish. | N/A (matcher ignored) |
| **`Stop`** | Fires when the agent execution loop terminates. | N/A (matcher ignored) |

### Matcher Regex Examples
- `""` or `"*"`: Matches all tools.
- `"run_command"`: Matches `run_command` tool exactly.
- `"run_command|view_file"`: Matches either `run_command` or `view_file`.
- `"browser_.*"`: Matches any tool starting with `browser_`.

---

## 3. Supported Tool Names by Category

### File and Directory Operations
- `view_file` (`AbsolutePath`, `StartLine`, `EndLine`, `IsSkillFile`)
- `write_to_file` (`TargetFile`, `Overwrite`, `CodeContent`, `Description`, `ArtifactMetadata`)
- `replace_file_content` (`TargetFile`, `Instruction`, `Description`, `AllowMultiple`, `TargetContent`, `ReplacementContent`, `StartLine`, `EndLine`)
- `multi_replace_file_content` (`TargetFile`, `Instruction`, `Description`, `ReplacementChunks`)
- `list_dir` (`DirectoryPath`)
- `find_by_name` (`SearchDirectory`, `Pattern`, `Type`, `Excludes`, `Extensions`, `FullPath`, `MaxDepth`)

### Search and Research
- `grep_search` (`SearchPath`, `Query`, `IsRegex`, `CaseInsensitive`, `Includes`, `MatchPerLine`)
- `search_web` (`query`, `domain`)
- `read_url_content` (`Url`)

### System and Execution
- `run_command` (`CommandLine`, `Cwd`, `WaitMsBeforeAsync`, `RunPersistent`, `RequestedTerminalID`)
- `manage_task` (`Action`, `TaskId`, `Input`)
- `schedule` (`DurationSeconds`, `CronExpression`, `MaxIterations`, `Prompt`)
- `list_permissions` ()
- `ask_permission` (`Action`, `Target`, `Reason`)

### Agent Collaboration
- `invoke_subagent` (`Subagents`)
- `define_subagent` (`name`, `description`, `system_prompt`, `enable_mcp_tools`, `enable_write_tools`, `enable_subagent_tools`)
- `send_message` (`Recipient`, `Message`)
- `manage_subagents` (`Action`, `ConversationIds`)

### Interaction and Media
- `ask_question` (`questions`)
- `generate_image` (`Prompt`, `ImageName`, `ImagePaths`)

---

## 4. Input & Output Protocol Contracts (stdin / stdout)

Hooks communicate via **JSON over stdin** (input) and **JSON over stdout** (output).

### Common Input Metadata (stdin)
Every hook payload includes these fields:
```json
{
  "conversationId": "ec33ebf9-0cba-4100-8142-c61503f6c587",
  "workspacePaths": ["/workspace/project"],
  "transcriptPath": "~/.gemini/antigravity/brain/ec33ebf9-0cba-4100-8142-c61503f6c587/.system_generated/logs/transcript.jsonl",
  "artifactDirectoryPath": "~/.gemini/antigravity/brain/ec33ebf9-0cba-4100-8142-c61503f6c587"
}
```

### Event Contracts

#### `PreToolUse`
- **stdin**: `toolCall` (`name`, `args`), `stepIdx`, common metadata.

```json
{
  "toolCall": {
    "name": "replace_file_content",
    "args": {
      "TargetFile": "/path/to/file.go",
      "TargetContent": "...",
      "ReplacementContent": "..."
    }
  },
  "stepIdx": 12,
  "conversationId": "...",
  "workspacePaths": ["..."]
}
```

- **stdout**:
```json
{
  "decision": "allow", // "allow" | "deny" | "ask" | "force_ask"
  "reason": "Allowed by safety checker.",
  "permissionOverrides": ["command(npm test)"]
}
```

> [!NOTE]
> **Hook Lifecycle & Session Initialization**:
> Workspace hooks in `hooks.json` are loaded into memory by the Antigravity agent process when the session initializes. Edits to `hooks.json` or hook scripts take effect when the agent session reloads.

#### `PostToolUse`
- **stdin**: `stepIdx`, `error` (empty string if success), common metadata.
- **stdout**: `{}`

#### `PreInvocation` & `PostInvocation`
- **stdin**: `invocationNum`, `initialNumSteps`, common metadata.
- **stdout**:
```json
{
  "injectSteps": [
    { "ephemeralMessage": "Maintain code style guidelines." }
  ],
  "terminationBehavior": "" // "" | "force_continue" | "terminate"
}
```

#### `Stop`
- **stdin**: `executionNum`, `terminationReason`, `error`, `fullyIdle`, common metadata.
- **stdout**:
```json
{
  "decision": "continue", // "continue" or "allow"
  "reason": "Verification steps still remaining."
}
```
