# Buffer Analytics Inquiry & Baseline Playbook

This reference establishes the standard analytical methodologies, inquiry types, and SQL formulas used to evaluate social post performance, diagnose anomalies, and benchmark content growth.

---

## 1. Outlier & Distribution Analysis (Mean vs. Median)

When evaluating day-of-week, topic, or channel performance, always compare the **Median** to the **Mean** to ensure viral spikes (e.g., 40k+ impression posts) do not distort baseline expectations.

### Methodology
- Calculate `COUNT`, `AVG` (Mean), `MEDIAN`, and `MAX` per cohort.
- Identify skew: If `Mean > 3 * Median`, performance is driven by rare outliers rather than a repeatable baseline.

### SQL / Python Template
```sql
SELECT
    day_of_week,
    COUNT(*) AS post_count,
    ROUND(AVG(impressions), 0) AS mean_impressions,
    MAX(impressions) AS max_impressions,
    ROUND(AVG(reactions), 1) AS mean_reactions
FROM v_posts_summary
WHERE status = 'sent' AND service = 'linkedin'
GROUP BY day_of_week;
```

---

## 2. Time-Series & Growth Tracking (Quarter-over-Quarter)

Determine whether reach, engagement rate, and audience response are compounding over time.

### Methodology
- Group posts by `year_month` or `quarter`.
- Track **Posting Frequency** against **Average Reach** to detect content fatigue or audience dilution.

### SQL Template
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

## 3. Geographic Sweet-Spot Inference

Since raw follower country geolocation is paywalled on basic tiers, infer geographic capture by mapping UTC publishing hours to global developer activity zones.

### Time Zones & Developer Activity Windows
- **11:00 – 15:00 UTC (Transatlantic Sweet Spot):**
  - UK / Europe: 12:00 – 16:00 (afternoon dwell time).
  - US East Coast: 07:00 – 10:00 EDT (morning commute / start-of-day feed check).
  - Brazil / LATAM: 08:00 – 11:00 BRT (morning startup).
- **17:00 – 21:00 UTC (US West Coast / Evening Catchup):**
  - US West Coast: 10:00 – 14:00 PDT.

---

## 4. Multi-Platform Top-Performer Trait Profiling

Extract the top 5–10 posts per platform and analyze their common structural DNA:

| Platform | Primary Ranking Metric | Winning Content Archetypes |
| :--- | :--- | :--- |
| **LinkedIn** | `impressions`, `reactions` | Contrast hooks (*"Six months ago X, today Y"*), Structured shifts (*First/Second/Third*), Humble discoveries (*"Neither did I!"*). |
| **Twitter / X** | `impressions`, `reposts`, `reactions` | Unfiltered conviction essays, Personal image/photo projects, High-impact industry predictions. |
| **Bluesky** | `reactions`, `reposts` | Architecture diagrams, Hand-drawn sketches, Deep Go philosophy quotes, Zero corporate marketing. |

---

## 5. Behavioral & Effort Allocation Bias Detection

Detect whether performance differences across days or formats are caused by the **calendar day** or by **author effort**:
- **Effort Bias:** Major long-form blog series and keynote decks are deliberately published on specific days (e.g. Mondays/Thursdays), giving those days an artificial performance advantage over casual mid-week check-ins.
- **Cadence vs. Saturation:** Posting $>5$ times a week can dilute median impressions per post, whereas 1–2 high-effort posts per week maximize reach per asset.
