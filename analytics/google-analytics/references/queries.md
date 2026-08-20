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
