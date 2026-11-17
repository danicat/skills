# Google Search Console authentication and OAuth setup guide

This guide walks through configuring Google Cloud Application Default Credentials (ADC) or `OAuth` 2.0 credentials to authorize Search Console ingestion into SQLite.

---

## 1. Prerequisites

1. **Google Account**: An account with verified ownership or read permissions on at least one property in [Google Search Console](https://search.google.com/search-console/).
2. **Google Cloud Project**: A project in [Google Cloud Console](https://console.cloud.google.com/).

---

## 2. Quick authentication via Application Default Credentials (ADC)

Read-only sync (`sync`) requests only `https://www.googleapis.com/auth/webmasters.readonly`:

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform
```

If you also submit XML sitemaps (`submit-sitemap`), include `https://www.googleapis.com/auth/webmasters` in your scopes, or use the desktop/web `OAuth` flow below.

---

## 3. Step-by-step GCP and OAuth configuration

### Step 1: Enable the Google Search Console API
1. Open the [Google Cloud Console API Library](https://console.cloud.google.com/apis/library).
2. Search for **Google Search Console API** (formerly Webmasters API).
3. Click **Enable**.

### Step 2: Configure the OAuth consent screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select User Type:
   - **External** (standard for personal Gmail or Google Workspace accounts).
   - **Internal** (if restricted to your Google Workspace organization).
3. Fill in basic app info:
   - **App name**: `Search Analytics Local App`
   - **User support email**: Your email address
   - **Developer contact**: Your email address
4. Click **Save and Continue**.
5. On the **Scopes** page, click **Add or Remove Scopes** and add:
   - `https://www.googleapis.com/auth/webmasters.readonly` (Read-only access to sites, sitemaps, and search analytics)
   - `https://www.googleapis.com/auth/webmasters` (Required for submitting XML sitemaps via `submit-sitemap`)
6. On the **Test users** page, click **+ Add Users** and enter your Google account email address.
7. Save and finish.

### Step 3: Create OAuth 2.0 client ID credentials
1. Go to **APIs & Services > Credentials**.
2. Click **+ Create Credentials > OAuth client ID**.
3. Select **Application type**: **Desktop app** (or **Web application** with redirect URIs `http://localhost:8080/oauth2callback` and `http://127.0.0.1:8080/oauth2callback`).
4. Set **Name**: `Search Analytics Local App`.
5. Click **Create** and download the client secret JSON file.

### Step 4: Save client secret
Copy the downloaded file to your local configuration folder:
```bash
mkdir -p ~/.config/gsc
cp ~/Downloads/client_secret_*.json ~/.config/gsc/client_secret.json
```

---

## 4. Authorization flow and token management

Once the client secret is placed at `~/.config/gsc/client_secret.json`, run the authorization flow:

```bash
uv run scripts/search_analytics.py auth --port 8080
```

1. If using a Web application client secret, open **`http://localhost:8080`** in your browser and click **Authorize with Google** (Desktop app secrets launch the local callback automatically).
2. Select your Google account and grant the requested permissions.
3. The CLI exchanges the authorization code for an **access token** and **refresh token**, persisting them to `~/.config/gsc/credentials.json` and refreshing automatically on later runs.
