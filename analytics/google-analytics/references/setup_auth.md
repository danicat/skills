# Google Analytics 4 authentication setup guide

The `google-analytics` skill connects to Google Analytics 4 using **Google Cloud Application Default Credentials (ADC)**, desktop OAuth credentials, or service account credentials.

---

## 1. Quick authentication via Application Default Credentials (ADC)

Read-only commands (`properties` and `sync`) require only the `analytics.readonly` scope:

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform
```

If you also create GA4 cloud reporting annotations (`annotate`), add `analytics.edit` to your OAuth scopes (`https://www.googleapis.com/auth/analytics.edit`), or run `uv run scripts/google_analytics.py auth`.

This writes your user OAuth credentials to `~/.config/gcloud/application_default_credentials.json`, which the CLI picks up automatically without extra environment variables.

---

## 2. Enable required Google Cloud APIs

Ensure the following APIs are enabled on your GCP project:

```bash
# Enable GA4 Admin and Data APIs
gcloud services enable analyticsadmin.googleapis.com analyticsdata.googleapis.com --project YOUR_PROJECT_ID
```

---

## 3. Grant GA4 property access

1. Open [Google Analytics](https://analytics.google.com).
2. Go to **Admin** (gear icon) -> **Property Access Management**.
3. Add the email address associated with your Google Cloud account as a **Viewer** (or **Editor** if creating cloud annotations).
4. Note your numeric **Property ID** under **Property Details** (e.g. `123456789`).

---

## 4. Environment variables

You can specify a default property ID via environment variable:

```bash
export GA4_PROPERTY_ID="123456789"
```
