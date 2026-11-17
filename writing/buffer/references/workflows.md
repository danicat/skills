# Canonical Buffer CLI workflows

Step-by-step shell and automation sequences with fail-fast error handling.

---

## 1. Timezone and account resolution

```bash
set -euo pipefail

# Read the account timezone directly and fail fast on missing output or invalid JSON
tz=$(buffer account --fields timezone --output json | jq -er '.timezone')
echo "Account timezone: $tz"
```

---

## 2. Safe post scheduling with approval gate

```bash
set -euo pipefail

# 1. Build and validate payload locally with --dry-run
payload=$(jq -nc \
  --arg ch "$channelId" \
  --arg t "Hello from the automated queue" \
  '{channelId: $ch, schedulingType: "automatic", mode: "addToQueue", text: $t, assets: []}')

buffer posts create --json "$payload" --dry-run

# 2. Show exact dispatch summary for explicit user approval before live mutation
echo "$payload" | jq '{channelId, mode, schedulingType, text, asset_count: (.assets | length)}'

# 3. Only after explicit user confirmation, run live creation:
# buffer posts create --json "$payload" --output json
```

---

## 3. Scheduled post at a specific local time

```bash
set -euo pipefail

# Build ISO-8601 string with local timezone offset
dueAt="2026-09-01T14:30:00-05:00"

buffer posts create \
  --channel-id "$channelId" \
  --scheduling-type automatic \
  --mode customScheduled \
  --due-at "$dueAt" \
  --text "Scheduled release announcement" \
  --dry-run

# Run without --dry-run (and with --output json) only after user confirmation
```

---

## 4. Bounded Relay pagination loop

```bash
set -euo pipefail

cursor=""
page_count=0
max_pages=50

while [ "$page_count" -lt "$max_pages" ]; do
  page_count=$((page_count + 1))

  if [ -n "$cursor" ]; then
    page=$(buffer posts list --channel-id "$channelId" --after "$cursor" --output json)
  else
    page=$(buffer posts list --channel-id "$channelId" --output json)
  fi

  echo "$page" | jq -c '.items[]'

  hasNext=$(echo "$page" | jq -er '.pageInfo.hasNextPage')
  if [ "$hasNext" != "true" ]; then
    break
  fi

  cursor=$(echo "$page" | jq -r '.pageInfo.endCursor // empty')
  if [ -z "$cursor" ]; then
    echo "Error: hasNextPage is true but endCursor is empty on page $page_count" >&2
    exit 1
  fi
done

if [ "${hasNext:-false}" = "true" ] && [ "$page_count" -ge "$max_pages" ]; then
  echo "Error: exceeded max_pages=$max_pages while paginating channel $channelId" >&2
  exit 1
fi
```

---

## 5. Multi-asset payload assembly and in-body links

For social networks where links inside the post body perform well alongside native media (such as LinkedIn, `Bluesky`, or Threads), place the canonical URL directly in `text` and attach hosted images or diagrams in `assets`:

```bash
set -euo pipefail

postText=$'We just published our architecture deep dive.\n\nRead the full walkthrough: https://example.com/project'

payload=$(jq -nc \
  --arg ch "$channelId" \
  --arg text "$postText" \
  --arg img1 "https://cdn.example.com/diagram-1.png" \
  --arg alt1 "System architecture overview diagram" \
  --arg img2 "https://cdn.example.com/benchmark-chart.png" \
  --arg alt2 "Latency benchmark comparison chart" \
  '{
    channelId: $ch,
    schedulingType: "automatic",
    mode: "addToQueue",
    text: $text,
    assets: [
      { image: { url: $img1, metadata: { altText: $alt1 } } },
      { image: { url: $img2, metadata: { altText: $alt2 } } }
    ]
  }')

# Verify asset count and URLs before asking for publish confirmation
echo "$payload" | jq '{channelId, mode, asset_count: (.assets | length), assets: [.assets[].image.url]}'
buffer posts create --json "$payload" --dry-run
```

If the user still wants a manual follow-up note copied locally after publishing (for example on plans without API-level reply support), detect the platform clipboard utility cleanly and fail fast if none is available:

```bash
copy_to_clipboard() {
  if command -v pbcopy >/dev/null; then
    pbcopy
  elif command -v wl-copy >/dev/null; then
    wl-copy
  elif command -v xclip >/dev/null; then
    xclip -selection clipboard
  elif command -v clip.exe >/dev/null; then
    clip.exe
  else
    echo "Error: no clipboard utility found (expected pbcopy, wl-copy, xclip, or clip.exe)" >&2
    return 1
  fi
}

cat << 'EOF' | copy_to_clipboard
Reference benchmarks:
https://example.com/benchmarks
EOF
```
