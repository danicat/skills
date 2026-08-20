# Google Analytics 4 Authentication Setup Guide

The `google-analytics` skill connects to Google Analytics 4 using **Google Cloud Application Default Credentials (ADC)** or service account credentials.

---

## 1. Quick Authentication via Application Default Credentials (ADC)

If you already have the Google Cloud SDK (`gcloud`) installed on your system:

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform
```

This writes your user OAuth credentials to `~/.config/gcloud/application_default_credentials.json`, which the CLI picks up automatically without additional environment variables.

---

## 2. Enabling Required Google Cloud APIs

Ensure the following APIs are enabled on your GCP project:

```bash
# Enable GA4 Admin and Data APIs
gcloud services enable analyticsadmin.googleapis.com analyticsdata.googleapis.com --project YOUR_PROJECT_ID
```

---

## 3. Granting GA4 Property Access

1. Open [Google Analytics](https://analytics.google.com).
2. Go to **Admin** (gear icon) $\rightarrow$ **Property Access Management**.
3. Add the email address associated with your Google Cloud account as a **Viewer** or **Administrator**.
4. Note your numeric **Property ID** under **Property Details** (e.g. `123456789`).

---

## 4. Environment Variables (Optional)

You can specify a default property ID via environment variable:

```bash
export GA4_PROPERTY_ID="123456789"
```
