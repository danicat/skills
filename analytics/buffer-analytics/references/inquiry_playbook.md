# Buffer analytics inquiry and baseline playbook

This reference sets out the statistical baselines, SQL formulas, and retrospective checks for evaluating post performance and diagnosing skew.

---

## 1. Outlier and distribution analysis (mean vs. median)

When comparing days, topics, or channels, compare the **median** against the **mean** so single viral posts do not distort baseline expectations.

### Methodology
- Calculate `COUNT`, `AVG` (mean), a window-function `MEDIAN`, and `MAX` per cohort.
- Check skew: when `mean > 3 * median`, a few outliers drive the cohort average.

### SQLite window-function median query
Because `SQLite` has no built-in `MEDIAN()` aggregate, rank rows with `ROW_NUMBER()` and average the middle one or two rows per partition:

```sql
WITH ranked AS (
    SELECT
        day_of_week,
        impressions,
        reactions,
        ROW_NUMBER() OVER (PARTITION BY day_of_week ORDER BY impressions) AS rn,
        COUNT(*) OVER (PARTITION BY day_of_week) AS cnt
    FROM v_posts_summary
    WHERE status = 'sent' AND service = 'linkedin' AND day_of_week IS NOT NULL
)
SELECT
    day_of_week,
    MAX(cnt) AS post_count,
    ROUND(AVG(impressions), 0) AS mean_impressions,
    ROUND(AVG(CASE WHEN rn IN ((cnt + 1) / 2, (cnt + 2) / 2) THEN impressions END), 0) AS median_impressions,
    MAX(impressions) AS max_impressions,
    ROUND(AVG(reactions), 1) AS mean_reactions
FROM ranked
GROUP BY day_of_week
ORDER BY median_impressions DESC;
```

---

## 2. Time-series and growth tracking (month-over-month)

Determine whether reach, engagement rate, and audience response are compounding over time.

### Methodology
- Group posts by `year_month` or quarter.
- Track **posting frequency** against **average reach** to spot fatigue or audience dilution.

### SQL template
```sql
SELECT
    service,
    strftime('%Y-%m', sent_at) AS year_month,
    COUNT(*) AS posts_published,
    ROUND(SUM(impressions), 0) AS total_impressions,
    ROUND(AVG(impressions), 0) AS avg_impressions_per_post,
    ROUND(AVG(reactions), 1) AS avg_reactions,
    ROUND(AVG(engagement_rate), 2) AS avg_engagement_rate
FROM v_posts_summary
WHERE status = 'sent'
GROUP BY service, year_month
ORDER BY service, year_month;
```

---

## 3. Geographic sweet-spot inference

Since raw follower country counts are often unavailable on basic API tiers, infer audience windows by mapping UTC publish hours to developer time zones.

### Time zones and developer activity windows
- **11:00 to 15:00 UTC (Transatlantic window):**
  - UK / Europe: `12:00 to 16:00` local afternoon dwell time.
  - US East Coast: `07:00 to 10:00` EDT morning feed check.
  - Brazil / LATAM: `08:00 to 11:00` BRT morning check-in.
- **17:00 to 21:00 UTC (US West Coast afternoon):**
  - US West Coast: `10:00 to 14:00` PDT.

---

## 4. Multi-platform top-performer trait profiling

Extract the top `5 to 10` posts per network and compare their structure:

| Platform | Primary Ranking Metric | Winning Content Archetypes |
| :--- | :--- | :--- |
| **LinkedIn** | `impressions`, `reactions` | Contrast hooks (*"Six months ago X, today Y"*), ordered breakdowns, honest engineering lessons. |
| **Twitter / X** | `impressions`, `reposts`, `reactions` | Short direct takeaways, real project screenshots or clips, concrete engineering predictions. |
| **`Bluesky`** | `reactions`, `reposts` | Architecture diagrams, handwritten sketches, concise technical quotes, zero corporate marketing. |

---

## 5. Behavioral and effort allocation bias detection

Separate genuine **calendar-day effects** from **author effort bias**:
- **Effort bias**: Long-form technical posts and announcements often launch on Mondays or Thursdays, inflating averages on those days over casual mid-week posts.
- **Cadence vs. saturation**: Publishing `> 5` posts per week can dilute median impressions per post, whereas `1 to 2` substantial posts per week protect reach per post.

---

## 6. Platform regime breaks and baseline hygiene

Social networks periodically rewrite their feed ranking and distribution systems. When a major distribution shift happens, historical impression averages stop acting as a valid benchmark.

### Rules for avoiding apples-to-oranges comparisons
- **Segment by distribution regime:** Never pool pre-shift and post-shift posts into a single baseline, and never judge post-shift raw impressions against pre-shift months or prior-year periods.
- **Known regime break (LinkedIn H2 2026):** In H2 2026, LinkedIn transitioned heavily from a connection-based Social Graph to an LLM-driven Interest Graph (widely tracked around the `360Brew` architecture), compressing broad 2nd- and 3rd-degree feed impressions across personal and company accounts.
- **Do not over-analyze incomplete post-shift windows:** Until H2 2026 finishes and a clean post-shift baseline exists, treat raw LinkedIn impression declines as a regime break rather than a content, topic, or audience failure. Avoid drawing strategic conclusions from partial post-shift months where no comparable baseline exists yet.
- **Diagnose distribution shift vs. content fatigue:** Always inspect `impressions` and `engagement_rate` side by side on substantive posts (`char_count >= 300`):
  - **Impressions down, `engagement_rate` flat or up:** Platform distribution compression. Fewer passive viewers see each post, while matched readers engage at the same or higher rate.
  - **Impressions down, `engagement_rate` also down (within the same regime):** Genuine hook, format, or audience mismatch.

### Diagnostic SQL template (substantive posts: reach vs. engagement rate by month)
```sql
SELECT
    service,
    year_month,
    COUNT(*) AS substantive_posts,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    MAX(impressions) AS max_impressions,
    ROUND(AVG(reactions + comments), 1) AS avg_interactions,
    ROUND(AVG(engagement_rate), 2) AS avg_engagement_rate
FROM v_posts_summary
WHERE status = 'sent'
  AND impressions > 0
  AND char_count >= 300
GROUP BY service, year_month
ORDER BY service, year_month;
```
