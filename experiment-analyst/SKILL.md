---
name: experiment-analyst
description: Analyze Tenkai agent experiments to find success factors, failure modes, and run patterns.
---

# Experiment Analyst

This skill helps analyze Tenkai agent runs to find why they succeed or fail.

## Core Rules

- Use data to back up all claims. Cite run IDs, exact errors, or metric differences.
- Do not mix up correlation with causation. For example, if failed runs often call `read_file`, it may be because agents use it to recover from errors, not because the tool itself is bad.
- Compare how different setups perform.

## Setup & Database

Set the database path before you run any tools or scripts:
```bash
export TENKAI_DB_PATH=agents/tenkai/experiments/tenkai.db
```

- `references/tenkai_db_schema.md`: Database structure details.
- `scripts/analyze_experiment.py`: Main analysis script for stats, tool usage, and success drivers.
- `scripts/analyze_patterns.py`: Script to rebuild agent workflows.
- `scripts/get_experiment_config.py`: Script to get the experiment settings.

## Analysis Steps

### 1. View the Settings
Check the configuration first:
```bash
python3 agents/tenkai/.gemini/skills/experiment-analyst/scripts/get_experiment_config.py <EXP_ID>
```
Look at what changed (like models, prompts, or tools) and what you expect to see.

### 2. View the Stats
Run the main script to get general metrics:
```bash
python3 agents/tenkai/.gemini/skills/experiment-analyst/scripts/analyze_experiment.py <EXP_ID>
```
Check "Success Determinants Analysis" to see which tools drive success or signal failure. Also find the most common errors.

### 3. Trace Run Patterns
Pick specific runs to study why they succeeded or failed:
```bash
python3 agents/tenkai/.gemini/skills/experiment-analyst/scripts/analyze_patterns.py <EXP_ID> "<ALTERNATIVE>"
```
- Look at successful runs. Did a specific tool prevent a bug?
- Look at failed runs. Did a tool run in an endless loop?
- Find how agents handle errors. Check if they read or edit files after a failure, or if they repeat the same mistake.

## Report Format

### Experiment X: [Name]

**Overview**
Brief summary of the experiment goals and the tested setups.

**Results**
| Alternative | Success Rate | Duration | Tokens | Key Feature |
|---|---|---|---|---|
| Variant A | ... | ... | ... | ... |

**Drivers & Signals**
- Drivers: Tools and patterns that increased success rates.
- Signals: Tools and patterns linked to failure.

**Detailed Workflow**
- Successful pattern: The steps taken in good runs. Example: `project_init` created folders and prevented path errors.
- Failure pattern: The steps taken in bad runs. Example: repeating a command on a file that does not exist.

**Conclusion & Actions**
- Best Variant: Which setup is better.
- Recommended Changes: Steps to fix the prompt or tools.
