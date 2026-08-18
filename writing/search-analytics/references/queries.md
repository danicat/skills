# Search Analytics SQL Query Cookbook

Run these queries using `python3 scripts/search_analytics.py query "<SQL>"` or directly in `sqlite3 ~/.gsc/analytics.db`.

---

## 1. High-Opportunity Optimization Targets (High Impressions, Low CTR)
Identifies search queries where your content already ranks on page 1 (positions 1–10) but receives a below-average click-through rate, making them prime candidates for better meta titles and descriptions:

```sql
SELECT 
    query,
    page,
    ROUND(SUM(impressions), 0) AS total_impressions,
    ROUND(SUM(clicks), 0) AS total_clicks,
    ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS ctr_pct,
    ROUND(AVG(position), 1) AS avg_rank
FROM v_search_performance
WHERE avg_position <= 10
GROUP BY query, page
HAVING SUM(impressions) >= 500 AND ctr_pct < 3.0
ORDER BY total_impressions DESC
LIMIT 20;
```

---

## 2. Keyword Cannibalization Detection
Finds queries where multiple different landing pages compete against each other for impressions:

```sql
SELECT 
    query,
    COUNT(DISTINCT page) AS competing_pages,
    GROUP_CONCAT(DISTINCT page) AS pages,
    ROUND(SUM(clicks), 0) AS total_clicks,
    ROUND(SUM(impressions), 0) AS total_impressions
FROM v_search_performance
WHERE query != ''
GROUP BY query
HAVING COUNT(DISTINCT page) > 1
ORDER BY total_impressions DESC
LIMIT 15;
```

---

## 3. Position-to-CTR Decay Curve
Calculates your actual click-through rate distribution across Google Search ranking positions (e.g. Rank 1 vs. Rank 2 vs. Rank 3):

```sql
SELECT 
    ROUND(avg_position) AS rank_bucket,
    ROUND(SUM(clicks), 0) AS clicks,
    ROUND(SUM(impressions), 0) AS impressions,
    ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS actual_ctr_pct
FROM v_search_performance
WHERE avg_position BETWEEN 1 AND 10
GROUP BY rank_bucket
ORDER BY rank_bucket ASC;
```

---

## 4. Mobile vs. Desktop Traffic Split
Compares search performance across device classes:

```sql
SELECT 
    device,
    COUNT(DISTINCT date) AS active_days,
    ROUND(SUM(clicks), 0) AS clicks,
    ROUND(SUM(impressions), 0) AS impressions,
    ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS ctr_pct,
    ROUND(AVG(avg_position), 1) AS avg_rank
FROM v_search_performance
GROUP BY device
ORDER BY clicks DESC;
```

---

## 5. Day-of-the-Week Traffic Trends
Evaluates whether developer/technical searches peak on weekdays or weekends:

```sql
SELECT 
    day_of_week,
    COUNT(DISTINCT date) AS day_count,
    ROUND(AVG(total_clicks), 1) AS avg_clicks_per_day,
    ROUND(AVG(total_impressions), 0) AS avg_impressions_per_day,
    ROUND(AVG(avg_ctr_pct), 2) AS avg_ctr_pct
FROM v_daily_summary
GROUP BY day_of_week
ORDER BY avg_clicks_per_day DESC;
```

---

## 6. Month-over-Month Growth Trajectory
Tracks total organic search impressions and clicks by month:

```sql
SELECT 
    year_month,
    COUNT(DISTINCT date) AS days_in_month,
    ROUND(SUM(clicks), 0) AS total_clicks,
    ROUND(SUM(impressions), 0) AS total_impressions,
    ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS monthly_ctr_pct,
    ROUND(AVG(position), 1) AS avg_rank
FROM search_performance
GROUP BY year_month
ORDER BY year_month ASC;
```
