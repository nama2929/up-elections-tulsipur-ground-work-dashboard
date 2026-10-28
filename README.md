# Saarthi Analytics — Tulsipur Ground Operations Portal

**Tulsipur Assembly 291** | Standalone, password-protected Streamlit portal.

Reuses the Manjhanpur ground-work dashboard's structure and Saarthi branding. In this first version, **no Google Sheets are connected**. No fake field figures are displayed.

## What's inside

- Saarthi logo splash/loading screen on a new session, followed by office password sign-in
- Manjhanpur-style navigation: **Home • Reports • Daily Summary • Team**
- Six prepared reporting sections (Daily Field Reports, Worker Registration, WhatsApp Outreach, Issues & Action Taken, Booth Visits, Social Media Reporting)
- Tulsipur-branded empty states where data will appear later
- Secure credential handling via Streamlit Secrets, with sign-out
- Responsive layout, suitable for desktop and phone

## Run locally (Windows / VS Code)

1. Unzip this folder and open it in VS Code.
2. Install the dependency:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Create a file named `.streamlit/secrets.toml`, using `.streamlit/secrets.toml.example` as a template, and **replace the placeholder password** with your chosen password.
4. Run:
   ```powershell
   python -m streamlit run app.py
   ```
5. Open the localhost address displayed in the terminal.

Alternatively set the environment variable `TULSIPUR_DASHBOARD_PASSWORD` rather than using `secrets.toml`.

## Deploy to Streamlit Community Cloud

1. Put all project files in a new GitHub repository. **Do not upload `.streamlit/secrets.toml`** (the `.gitignore` already excludes it).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app, choose that repository, set the entry point to `app.py`, and deploy.
3. Under **App settings → Secrets**, paste:
   ```toml
   dashboard_password = "YOUR_CHOSEN_PASSWORD"
   ```
4. Reboot the app if prompted. Visitors will see the Saarthi splash followed by the password gate.

**Important:** Your original Manjhanpur login password has *not* been copied, and no Google service-account credentials or sheet IDs are included.

## When you're ready for Sheets

Add the Tulsipur coordinator list and approved Google Sheet IDs to `config.py`, then implement a data loader for the matching reporting sections. This version intentionally makes no API calls to Google Sheets and contains no private report data.

## Project files

- `app.py` — visual portal, splash, password and navigation
- `config.py` — prepared reporting sections and empty connection settings
- `assets/saarthi-logo.png` — Saarthi logo reused from supplied branded presentation
- `.streamlit/config.toml` — theme
- `.streamlit/secrets.toml.example` — safe password configuration sample
- `requirements.txt` — dependency
