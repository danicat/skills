# Buffer Pitfalls & Common Traps

Skim this reference before composing commands and JSON payloads for Buffer CLI.

---

## 1. Scheduling Traps

- **`mode: addToQueue` is queued, not immediate**: Use `mode: shareNow` to publish immediately. `mode: shareNext` jumps to the front of the queue. `mode: customScheduled` requires `dueAt`.
- **`schedulingType: notification` does not auto-publish**: It sends a push notification to the mobile app for a human to publish. Use `schedulingType: automatic` for hands-off publishing.
- **`addToQueue` on a channel with no schedule**: Silently lands in an empty queue slot. Inspect the channel schedule with `buffer channels get --id <id>` first.
- **All times are ISO-8601 with offset**: `dueAt` must include a timezone offset (e.g. `2026-05-06T17:00:00-05:00`). Compute the offset from `buffer config get timezone` or `buffer account --fields timezone`. Never assume UTC.

---

## 2. Identifier Integrity

- **Never guess channel IDs**: Always fetch with `buffer channels list --output json`. IDs look pseudo-random; invalid IDs will be accepted initially and fail on execution with vague errors.
- **IDs are not portable across organizations**: A `channelId` from Organization A cannot be used while authenticated against Organization B.

---

## 3. Input & Payload Formatting

- **`--json` overrides flags entirely**: When both `--json` and individual flags are supplied, flags are dropped. Pick one style per command.
- **Nested objects need `--json`**: Per-service `metadata.*` and `assets.*` cannot be set via flat flags. Use the JSON path.
- **Empty `text` without assets is rejected**: Most channels require text or at least one image/video asset.
- **Control characters are rejected**: Strip ASCII control characters (`U+0000`–`U+001F` except whitespace) before sending.

---

## 4. Per-Service Minimum Payloads

| Service | Minimum Required Payload Elements |
| :--- | :--- |
| **Twitter / X, Mastodon, Threads, Bluesky** | `text` only |
| **LinkedIn** | `text` or `assets`; documents require `metadata.linkedin.linkAttachment` |
| **Instagram** | Image or video asset; `metadata.instagram.type` + `metadata.instagram.shouldShareToFeed` |
| **Facebook** | `text` or `assets` |
| **TikTok** | Image or video asset |
| **Pinterest** | Image asset + `metadata.pinterest.boardServiceId` (from `channels get`) |
| **YouTube** | Video asset + `metadata.youtube.title` + `metadata.youtube.categoryId` |

---

## 5. Twitter / X Threads

When composing multi-post chains for Twitter/X via `metadata.twitter.thread`:
- The outer `text` **MUST** equal the first thread item's `text`:
```json
{
  "text": "First tweet in thread",
  "metadata": {
    "twitter": {
      "thread": [
        { "text": "First tweet in thread" },
        { "text": "Second tweet in thread" }
      ]
    }
  }
}
```
