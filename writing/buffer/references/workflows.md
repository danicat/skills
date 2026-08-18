# Canonical Buffer CLI Workflows

Step-by-step shell and agent automation sequences.

---

## 1. Timezone & Account Resolution

```bash
# Read persisted timezone or fallback to account fetch
tz=$(buffer config get timezone --output json 2>/dev/null | jq -r '.value // empty')
if [ -z "$tz" ] || [ "$tz" = "null" ]; then
  tz=$(buffer account --fields timezone --output json | jq -r '.timezone')
fi
```

---

## 2. Safe Post Scheduling

```bash
# 1. Build and validate payload with --dry-run
payload=$(jq -nc \
  --arg ch "$channelId" \
  --arg t "Hello from the automated queue" \
  '{channelId: $ch, schedulingType: "automatic", mode: "addToQueue", text: $t}')

buffer posts create --json "$payload" --dry-run

# 2. Dispatch live mutation
buffer posts create --json "$payload" --output json
```

---

## 3. Scheduled Post at Specific Local Time

```bash
# Build ISO-8601 string with local timezone offset
dueAt="2026-09-01T14:30:00-05:00"

buffer posts create --channel-id "$channelId" \
  --scheduling-type automatic \
  --mode customScheduled \
  --due-at "$dueAt" \
  --text "Scheduled release announcement" \
  --output json
```

---

## 4. Relay Pagination Loop

```bash
cursor=""
while :; do
  page=$(buffer posts list ${cursor:+--after "$cursor"} --output json)
  echo "$page" | jq -c '.items[]'
  hasNext=$(echo "$page" | jq -r '.pageInfo.hasNextPage')
  cursor=$(echo "$page" | jq -r '.pageInfo.endCursor')
  [ "$hasNext" = "true" ] || break
done
```

---

## 5. Free-Tier First Comment Clipboard Pipeline

When publishing to networks like LinkedIn where first-comment links avoid feed penalties, but the automated `metadata.linkedin.firstComment` API is gated behind a paid plan:

```bash
# 1. Publish immediately
result=$(buffer posts create --channel-id "$channelId" \
  --scheduling-type automatic \
  --mode shareNow \
  --text "$mainPostText" \
  --output json)

# 2. Pipe the first comment directly to the OS clipboard
cat << 'EOF' | pbcopy
Links mentioned in the post:
https://example.com/project
EOF

# 3. Output the live URL so the user can paste immediately (Cmd+V)
echo "$result" | jq -r '.post.externalLink'
```

