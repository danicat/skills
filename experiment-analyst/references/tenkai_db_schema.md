# Tenkai Database Schema (`tenkai.db`)

This document describes the Tenkai database schema to help write SQL queries.

## Tables

### `experiments`
Experiment metadata.
- **`id`**: Primary Key (FK in `run_results.experiment_id`).
- **`name`**: Human-readable name.
- **`config_content`**: YAML configuration.

### `run_results`
Run results. Each row represents one run of a specific alternative.
- **`id`**: Primary Key.
- **`experiment_id`**: FK to `experiments`.
- **`alternative`**: Variant name (for example, "default", "godoctor-mcp").
- **`is_success`**: 1 if validation passed, 0 if it failed.
- **`duration`**: Execution time in nanoseconds (divide by 1e9 for seconds).
- **`total_tokens`**: Total tokens consumed.
- **`tool_calls_count`**: Total tool calls.
- **`failed_tool_calls`**: Count of tool calls that returned an error.
- **`status`**: "COMPLETED", "ABORTED", or other status string.
- **`reason`**: "SUCCESS", "FAILED (VALIDATION)", "FAILED (TIMEOUT)", or other reason.

### `run_events`
Event logs for all runs.
- **`run_id`**: FK to `run_results`.
- **`type`**: Event type ("tool", "message", "error").
- **`payload`**: JSON string with event details.
    - For `tool`: `{"name": "...", "args": {...}, "output": "...", "status": "..."}`
    - For `message`: `{"role": "...", "content": "..."}`

## Views

### `tool_usage`
Tool calls from `run_events` where type is 'tool'.
- **`run_id`**: FK to `run_results`.
- **`name`**: Tool name.
- **`args`**: JSON arguments.
- **`output`**: Tool stdout or error message.
- **`status`**: "success" or "error".

## Queries

**1. Performance Summary by Alternative**
```sql
SELECT 
    alternative, 
    COUNT(*) as total, 
    SUM(is_success) as successes, 
    AVG(duration)/1e9 as avg_dur, 
    AVG(total_tokens) as avg_tok 
FROM run_results 
WHERE experiment_id = ? 
GROUP BY alternative;
```

**2. Tool Usage Stats**
```sql
SELECT 
    r.alternative,
    tu.name,
    COUNT(*) as count
FROM run_results r
JOIN tool_usage tu ON r.id = tu.run_id
WHERE r.experiment_id = ?
GROUP BY r.alternative, tu.name;
```
