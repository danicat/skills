# Skills Library

This repository is a collection of specialized **Agent Skills** for the Gemini CLI. Each skill provides on-demand expertise, procedural workflows, and task-specific resources to extend your agent's capabilities.

## Available Skills

- **`experiment-analyst`**: Expert data scientist and systems engineer for analyzing agent experiments. Identifies success factors, failure modes, and behavioral patterns from experiment databases.

## Installation

You can install any skill from this library directly using the Gemini CLI:

```bash
# Install to User scope (~/.gemini/skills)
gemini skills install git@github.com:danicat/skills.git --path <skill-name>

# Install to Workspace scope (.gemini/skills)
gemini skills install git@github.com:danicat/skills.git --path <skill-name> --scope workspace
```

## Creating a New Skill

A skill is a self-contained directory that packages instructions and assets.

### Recommended Structure
- `SKILL.md`: (Required) Metadata and expert procedural guidance.
- `scripts/`: Executable tools used by the skill.
- `references/`: Documentation, schemas, or examples.
- `assets/`: Templates or binary resources.

To contribute a new skill, create a folder following this structure and ensure the `SKILL.md` has the required frontmatter (`name` and `description`).

---
For more information on the Agent Skills standard, visit [agentskills.io](https://agentskills.io).
