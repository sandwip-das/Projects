# Social Login Setup

To make Google and Facebook login work, you need to configure your Developer Console for each provider and update `settings.py` with the keys.

## 1. Google Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new Project.
3. Search for "Google+ API" and "Google People API" and enable them.
4. Go to **Credentials -> Create Credentials -> OAuth Client ID**.
5. Application Type: **Web application**.
6. **Authorized JavaScript origins**: `http://127.0.0.1:8000`
7. **Authorized redirect URIs**: `http://127.0.0.1:8000/accounts/google/login/callback/`
8. Copy the **Client ID** and **Client Secret**.
9. Open `ecomm/settings.py` and replace `YOUR_GOOGLE_CLIENT_ID` and `YOUR_GOOGLE_SECRET`.

## 2. Facebook Setup
1. Go to [Meta for Developers](https://developers.facebook.com/).
2. Create a new App (Type: Consumer).
3. Add **Facebook Login** product.
4. Settings > Basic > App Domains: `127.0.0.1`.
5. Product Settings > Facebook Login > Settings > **Valid OAuth Redirect URIs**: `http://127.0.0.1:8000/accounts/facebook/login/callback/`
6. Copy the **App ID** and **App Secret**.
7. Open `ecomm/settings.py` and replace `YOUR_FACEBOOK_CLIENT_ID` and `YOUR_FACEBOOK_SECRET`.

## 3. Restart Server
After updating settings, restart the server for changes to take effect.
