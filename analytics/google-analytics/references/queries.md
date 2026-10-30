# Google Analytics 4 SQL Query Cookbook

Execute these queries using `uv run scripts/google_analytics.py query "<SQL>" --db <path_to_db> --format markdown`.

---

## 1. Top Articles by Reading Depth & Active Dwell Time

```sql
SELECT
    page_path,
    page_title,
    total_views,
    total_users,
    avg_dwell_sec || 's' AS avg_dwell,
    total_dwell_min || 'm' AS total_dwell,
    avg_bounce_pct || '%' AS bounce_pct
FROM v_page_performance
ORDER BY total_dwell_min DESC
LIMIT 15;
```

---

## 2. Path & Subdirectory Performance Comparison (e.g. `/docs/`, `/blog/`, `/tutorials/`)

```sql
SELECT
    CASE
        WHEN page_path LIKE '/docs/%' THEN 'Documentation'
        WHEN page_path LIKE '/blog/%' OR page_path LIKE '/posts/%' THEN 'Articles / Blog'
        WHEN page_path LIKE '/tutorials/%' THEN 'Tutorials'
        WHEN page_path = '/' THEN 'Homepage'
        ELSE 'Other'
    END AS content_category,
    COUNT(DISTINCT page_path) AS page_count,
    SUM(total_views) AS total_page_views,
    SUM(total_users) AS unique_readers,
    ROUND(SUM(total_dwell_min), 1) AS total_dwell_minutes,
    ROUND(SUM(total_dwell_min) * 60.0 / MAX(SUM(total_users), 1), 1) AS avg_dwell_per_user_sec,
    ROUND(AVG(avg_bounce_pct), 1) AS avg_bounce_pct
FROM v_page_performance
GROUP BY content_category
ORDER BY total_page_views DESC;
```

---

## 3. Geographic Audience Distribution (Top Countries by Engagement)

```sql
SELECT
    country,
    SUM(sessions) AS total_sessions,
    SUM(active_users) AS total_users,
    SUM(screen_page_views) AS total_page_views,
    ROUND(SUM(user_engagement_duration) / MAX(SUM(active_users), 1), 1) AS avg_dwell_sec,
    ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_pct
FROM daily_pages
WHERE country IS NOT NULL AND country != '' AND country != '(not set)'
GROUP BY country
ORDER BY total_sessions DESC
LIMIT 10;
```

---

## 4. Top Traffic Channels & Conversion Engagement Rate

```sql
SELECT
    channel_group,
    source_medium,
    SUM(total_sessions) AS sessions,
    SUM(total_users) AS users,
    SUM(total_new_users) AS new_users,
    ROUND(AVG(engagement_rate_pct), 1) || '%' AS avg_engagement_rate,
    ROUND(AVG(avg_dwell_sec), 1) || 's' AS avg_dwell,
    ROUND(AVG(engaged_dwell_sec), 1) || 's' AS engaged_dwell,
    ROUND(SUM(total_dwell_min), 1) AS total_dwell_min
FROM v_channel_performance
GROUP BY channel_group, source_medium
HAVING SUM(total_sessions) >= 50
ORDER BY sessions DESC;
```

---

## 5. Day-of-the-Week Traffic Trends

```sql
SELECT
    CASE CAST(strftime('%w', date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    COUNT(DISTINCT date) AS day_count,
    ROUND(AVG(total_sessions), 0) AS avg_sessions,
    ROUND(AVG(total_active_users), 0) AS avg_users,
    ROUND(AVG(total_page_views), 0) AS avg_page_views,
    ROUND(AVG(total_engagement_min), 1) AS avg_dwell_min
FROM v_daily_summary
GROUP BY strftime('%w', date)
ORDER BY avg_sessions DESC;
```

---

## 6. Month-over-Month Growth Trajectory

```sql
SELECT
    strftime('%Y-%m', date) AS month,
    SUM(screen_page_views) AS views,
    SUM(sessions) AS sessions,
    SUM(active_users) AS users,
    ROUND(SUM(user_engagement_duration) / 60.0, 1) AS total_dwell_min
FROM daily_pages
GROUP BY month
ORDER BY month DESC;
```

---

## 7. Outbound Exit Clicks to Developer & External Resources

```sql
SELECT
    link_url,
    total_clicks,
    total_users,
    referring_pages_count
FROM v_outbound_links
ORDER BY total_clicks DESC
LIMIT 15;
```

---

## 8. Discovery Channel Split: Organic Search vs. Generative AI vs. Social Referrals

GA4's built-in `session_default_channel_group` groups LLM assistants (`chatgpt.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com`, `copilot.microsoft.com`) under generic `Referral` or `Organic Search`. This query splits discovery traffic into explicit buckets and compares raw session dwell against engaged session dwell:

```sql
SELECT
    CASE
        WHEN LOWER(session_source_medium) LIKE '%chatgpt%'
          OR LOWER(session_source_medium) LIKE '%perplexity%'
          OR LOWER(session_source_medium) LIKE '%claude%'
          OR LOWER(session_source_medium) LIKE '%gemini.google%'
          OR LOWER(session_source_medium) LIKE '%copilot%'
          OR LOWER(session_source_medium) LIKE '%edgeservices.bing%'
          OR LOWER(session_source_medium) LIKE '%mistral%'
          OR LOWER(session_source_medium) LIKE '%you.com%'
        THEN 'Generative AI'
        WHEN session_default_channel_group = 'Organic Search'
          OR LOWER(session_source_medium) LIKE '%/ organic%'
        THEN 'Organic Search'
        WHEN session_default_channel_group IN ('Organic Social', 'Paid Social')
          OR LOWER(session_source_medium) LIKE '%linkedin%'
          OR LOWER(session_source_medium) LIKE '%twitter%'
          OR LOWER(session_source_medium) LIKE '%t.co%'
          OR LOWER(session_source_medium) LIKE '%x.com%'
          OR LOWER(session_source_medium) LIKE '%bsky%'
          OR LOWER(session_source_medium) LIKE '%reddit%'
          OR LOWER(session_source_medium) LIKE '%news.ycombinator%'
          OR LOWER(session_source_medium) LIKE '%facebook%'
          OR LOWER(session_source_medium) LIKE '%mastodon%'
          OR LOWER(session_source_medium) LIKE '%threads%'
        THEN 'Social Referrals'
        WHEN session_default_channel_group = 'Referral'
        THEN 'Web Referrals'
        ELSE 'Direct / Other'
    END AS discovery_channel,
    SUM(sessions) AS sessions,
    SUM(active_users) AS users,
    SUM(new_users) AS new_users,
    SUM(engaged_sessions) AS engaged_sessions,
    ROUND(SUM(engaged_sessions) * 100.0 / MAX(SUM(sessions), 1), 1) AS engagement_rate_pct,
    ROUND(SUM(user_engagement_duration) / MAX(SUM(sessions), 1), 1) AS avg_dwell_sec,
    CASE WHEN SUM(engaged_sessions) > 0 THEN ROUND(SUM(user_engagement_duration) / SUM(engaged_sessions), 1) ELSE 0.0 END AS engaged_dwell_sec
FROM daily_traffic
GROUP BY discovery_channel
ORDER BY sessions DESC;
```

---

## 9. Unengaged `Direct` Traffic & Automated Scraper Outlier Detection

Headless crawlers, link previewers, and cloud monitors typically omit the HTTP `Referer` header (landing in `Direct`) and exit without firing a second interaction event (`<2s` dwell and `<10%` engagement rate). Run this diagnostic before computing site-wide averages to identify synthetic `Direct` spikes by country and month:

```sql
SELECT
    strftime('%Y-%m', date) AS month,
    country,
    device_category,
    SUM(sessions) AS direct_sessions,
    SUM(engaged_sessions) AS engaged_sessions,
    ROUND(SUM(engaged_sessions) * 100.0 / MAX(SUM(sessions), 1), 1) AS engagement_rate_pct,
    ROUND(SUM(user_engagement_duration) / MAX(SUM(sessions), 1), 1) AS avg_dwell_sec
FROM daily_traffic
WHERE session_default_channel_group = 'Direct'
GROUP BY month, country, device_category
HAVING SUM(sessions) >= 50
   AND (
       (SUM(engaged_sessions) * 100.0 / MAX(SUM(sessions), 1)) < 15.0
       OR (SUM(user_engagement_duration) / MAX(SUM(sessions), 1)) < 2.0
   )
ORDER BY direct_sessions DESC;
```

---

## 10. Custom & Enhanced Telemetry Event Inventory

GA4 stores both automatic lifecycle events and custom instrumentation in `daily_events`. Run this inventory query to discover all enhanced and custom interaction events (such as `scroll`, `click`, `code_copy`, `scroll_25`, `scroll_50`, `scroll_75`, or `form_submit`) alongside the number of distinct pages where each event fired:

```sql
SELECT
    event_name,
    SUM(event_count) AS total_events,
    SUM(total_users) AS total_users,
    COUNT(DISTINCT page_path) AS distinct_pages,
    MIN(date) AS first_seen,
    MAX(date) AS last_seen
FROM daily_events
WHERE event_name NOT IN ('page_view', 'user_engagement', 'session_start', 'first_visit')
GROUP BY event_name
ORDER BY total_events DESC;
```

---

## 11. Page-Level Reading Funnel (Dwell Time + Scroll Depth + Outbound Clicks)

Because GA4 calculates `user_engagement_duration` as the time elapsed between `session_start` and the final engagement event, single-page sessions that exit without a second event record `0s` duration. Joining `daily_pages` with `daily_events` (`scroll` and custom events) and `outbound_clicks` provides a complete reading funnel per page:

```sql
WITH page_totals AS (
    SELECT
        page_path,
        MAX(page_title) AS page_title,
        SUM(screen_page_views) AS views,
        SUM(active_users) AS users,
        SUM(sessions) AS sessions,
        SUM(user_engagement_duration) AS duration_sec
    FROM daily_pages
    GROUP BY page_path
),
event_totals AS (
    SELECT
        page_path,
        SUM(CASE WHEN event_name = 'scroll' THEN event_count ELSE 0 END) AS scroll_90_events,
        SUM(CASE WHEN event_name NOT IN ('page_view', 'user_engagement', 'session_start', 'first_visit', 'scroll', 'click') THEN event_count ELSE 0 END) AS custom_events
    FROM daily_events
    GROUP BY page_path
),
outbound_totals AS (
    SELECT
        page_path,
        SUM(event_count) AS outbound_clicks
    FROM outbound_clicks
    GROUP BY page_path
)
SELECT
    p.page_path,
    p.page_title,
    p.views,
    p.users,
    ROUND(p.duration_sec / MAX(p.users, 1), 1) AS dwell_per_user_sec,
    COALESCE(e.scroll_90_events, 0) AS scroll_90_events,
    ROUND(COALESCE(e.scroll_90_events, 0) * 100.0 / MAX(p.users, 1), 1) AS scroll_per_user_pct,
    COALESCE(e.custom_events, 0) AS custom_events,
    COALESCE(o.outbound_clicks, 0) AS outbound_clicks,
    ROUND(COALESCE(o.outbound_clicks, 0) * 100.0 / MAX(p.users, 1), 1) AS outbound_ctr_pct
FROM page_totals p
LEFT JOIN event_totals e ON p.page_path = e.page_path
LEFT JOIN outbound_totals o ON p.page_path = o.page_path
ORDER BY p.views DESC
LIMIT 15;
```
