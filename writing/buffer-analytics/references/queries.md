# Buffer Analytics SQL Recipes & Query Cookbooks

All queries can be executed directly using the helper script:
```bash
python3 scripts/buffer_analytics.py query "<SQL>" --format markdown
```

---

## 1. Top Performing Posts by Reach & Impressions

```sql
SELECT 
    service,
    sent_date,
    CAST(impressions AS INTEGER) AS impressions,
    CAST(reactions AS INTEGER) AS reactions,
    CAST(comments AS INTEGER) AS comments,
    engagement_rate,
    SUBSTR(text, 1, 90) AS opening_hook
FROM v_posts_summary
WHERE status = 'sent' AND impressions > 0
ORDER BY impressions DESC
LIMIT 15;
```

---

## 2. Best Days of the Week to Post (by Network)

```sql
SELECT 
    service,
    day_of_week,
    COUNT(*) AS total_posts,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions,
    ROUND(AVG(comments), 1) AS avg_comments,
    ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
FROM v_posts_summary
WHERE status = 'sent' AND day_of_week IS NOT NULL
GROUP BY service, day_of_week
ORDER BY service, avg_impressions DESC;
```

---

## 3. Best Hours of the Day (UTC)

```sql
SELECT 
    service,
    hour_of_day || ':00 UTC' AS posting_hour,
    COUNT(*) AS total_posts,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions,
    ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
FROM v_posts_summary
WHERE status = 'sent' AND impressions > 0
GROUP BY service, hour_of_day
HAVING COUNT(*) >= 3
ORDER BY avg_impressions DESC;
```

---

## 4. Impact of External Links on Organic Distribution

Compare posts with links in the body vs. posts without links (e.g. first comment strategy):

```sql
SELECT 
    service,
    CASE WHEN has_link = 1 THEN 'Link in Body' ELSE 'No Link / Link in Comment' END AS link_placement,
    COUNT(*) AS post_count,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions,
    ROUND(AVG(comments), 1) AS avg_comments,
    ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
FROM v_posts_summary
WHERE status = 'sent' AND impressions > 0
GROUP BY service, has_link;
```

---

## 5. Post Length vs. Performance (Short vs Medium vs Long-Form)

```sql
SELECT 
    service,
    CASE 
        WHEN char_count < 280 THEN 'Short (<280 chars)'
        WHEN char_count BETWEEN 280 AND 800 THEN 'Medium (280-800 chars)'
        ELSE 'Long-form (>800 chars)'
    END AS post_length_cohort,
    COUNT(*) AS post_count,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions,
    ROUND(AVG(comments), 1) AS avg_comments,
    ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
FROM v_posts_summary
WHERE status = 'sent' AND impressions > 0
GROUP BY service, post_length_cohort
ORDER BY service, avg_impressions DESC;
```

---

## 6. Keyword & Topic Cohort Analysis

Analyze performance across specific topics (e.g. Go, Gemini, Agents, Gaming):

```sql
SELECT 
    CASE 
        WHEN LOWER(text) LIKE '%golang%' OR LOWER(text) LIKE '%#golang%' OR LOWER(text) LIKE '%go develop%' THEN 'Go / Golang'
        WHEN LOWER(text) LIKE '%subagent%' OR LOWER(text) LIKE '%swarm%' OR LOWER(text) LIKE '%agent%' THEN 'AI Agents / Antigravity'
        WHEN LOWER(text) LIKE '%game%' OR LOWER(text) LIKE '%atari%' OR LOWER(text) LIKE '%playstation%' THEN 'Gaming / GameDev'
        WHEN LOWER(text) LIKE '%batch api%' OR LOWER(text) LIKE '%pricing%' OR LOWER(text) LIKE '%cheaper%' THEN 'Cost & Benchmarks'
        ELSE 'General / Other'
    END AS topic,
    COUNT(*) AS total_posts,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions,
    ROUND(AVG(comments), 1) AS avg_comments,
    ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
FROM v_posts_summary
WHERE status = 'sent' AND service = 'linkedin'
GROUP BY topic
ORDER BY avg_impressions DESC;
```
