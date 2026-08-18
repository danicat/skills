# Google Search Console OAuth 2.0 & API Setup Guide

This guide walks through configuring Google Cloud OAuth 2.0 credentials to authorize your client application and ingest real Search Console analytics into SQLite.

---

## 1. Prerequisites

1. **Google Account**: An account with verified ownership or read permissions on at least one property in [Google Search Console](https://search.google.com/search-console/).
2. **Google Cloud Project**: A project in [Google Cloud Console](https://console.cloud.google.com/).

---

## 2. Step-by-Step GCP Configuration

### Step 1: Enable the Google Search Console API
1. Open the [Google Cloud Console API Library](https://console.cloud.google.com/apis/library).
2. Search for **Google Search Console API** (formerly Webmasters API).
3. Click **Enable**.

### Step 2: Configure the OAuth Consent Screen
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
   - `https://www.googleapis.com/auth/webmasters` (Full management access)
6. On the **Test users** page, click **+ Add Users** and enter your Google account email address.
7. Save and finish.

### Step 3: Create OAuth 2.0 Client ID Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **+ Create Credentials > OAuth client ID**.
3. Select **Application type**: **Web application**.
4. Set **Name**: `Search Analytics Local App`.
5. Under **Authorized redirect URIs**, add both:
   - `http://localhost:8080/oauth2callback`
   - `http://127.0.0.1:8080/oauth2callback`
6. Click **Create**.
7. Download the client secret JSON file.

### Step 4: Save Client Secret
Copy the downloaded file to your local configuration folder:
```bash
mkdir -p ~/.config/gsc
cp ~/Downloads/client_secret_*.json ~/.config/gsc/client_secret.json
```

---

## 3. Authorization Flow & Token Management

Once the client secret is placed at `~/.config/gsc/client_secret.json`, start the companion server:

```bash
python3 scripts/search_analytics.py auth --port 8080
```

1. Open **`http://localhost:8080`** in your browser.
2. Click **Authorize with Google**.
3. Select your Google account and grant the requested permissions.
4. Google redirects to `/oauth2callback`, exchanges the authorization code for an **access token** and **refresh token**, and automatically persists them to:
   `~/.config/gsc/credentials.json`

The CLI utility will automatically refresh the access token using the stored refresh token on all subsequent runs.
