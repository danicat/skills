# Google Analytics 4 authentication setup guide

The `google-analytics` skill connects to Google Analytics 4 using **OAuth 2.0 client credentials** (`~/.config/ga4/credentials.json`), **Google Cloud Application Default Credentials (ADC)**, or service account credentials.

---

## 1. Recommended: OAuth 2.0 desktop login (`auth`)

Run the bundled OAuth flow once to persist credentials (including `refresh_token` and UTC `expiry`) to `~/.config/ga4/credentials.json` so commands work across any working directory and refresh tokens automatically before expiring:

1. Place your Desktop OAuth client secret JSON at `~/.config/ga4/client_secret.json` (or `~/.config/gcloud/analytics_oauth_client.json`).
2. Authorize `analytics.readonly` and `analytics.edit` scopes:

```bash
uv run scripts/google_analytics.py auth --port 8080
```

When `~/.config/ga4/credentials.json` is absent and no `./credentials.json` exists in the current directory, both `auth` and API commands default to `~/.config/ga4/credentials.json` (creating parent directories automatically).

---

## 2. Alternative: Application Default Credentials (ADC)

Read-only commands (`properties` and `sync`) require the `analytics.readonly` scope:

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform
```

If you also create GA4 cloud reporting annotations (`annotate`), add `analytics.edit` to your OAuth scopes (`https://www.googleapis.com/auth/analytics.edit`), or run `uv run scripts/google_analytics.py auth`.

This writes your user OAuth credentials to `~/.config/gcloud/application_default_credentials.json`. Note that default `gcloud auth application-default login` tokens without `--scopes ...analytics.readonly` will fail with `403 ACCESS_TOKEN_SCOPE_INSUFFICIENT`.

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
