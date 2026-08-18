# Buffer Rate Limits & Idempotency

Operational limits, 429 backoff procedures, and retry rules for agent pipelines.

---

## Rate Limit Windows

Buffer enforces three stacked rate-limiting windows per API token:

| Window | Duration | Scope / Purpose |
| :--- | :--- | :--- |
| **`15m`** | 15 minutes | Burst protection |
| **`24h`** | 24 hours | Daily fairness |
| **`30d`** | 30 days | Account monthly quota |

### Handling HTTP 429 & Backoff

On rate limit trip (Exit Code `3`):
1. Extract `Retry-After` seconds from the stderr error message.
2. Sleep for the specified duration.
3. Retry once. If another 429 occurs, double the sleep interval and retry once more.

---

## Idempotency & Retry Matrix

| Command Group | Idempotent? | Retry Strategy on Failure |
| :--- | :---: | :--- |
| `account`, `channels list`, `channels get` | **Yes** | Safe to retry immediately |
| `posts list`, `posts get`, `dailyPostingLimits` | **Yes** | Safe to retry immediately |
| `posts create` | **NO** | Search recent posts via `posts list` before retrying |
| `ideas create` | **NO** | Inspect existing ideas before re-issuing |
| `posts delete` | **Yes** (effectively) | Second call returns exit 3 ("not found") |
