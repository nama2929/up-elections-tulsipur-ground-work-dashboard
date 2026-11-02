# Saarthi Analytics — Tulsipur Gram Panchayat Reports

Streamlit app for **Tulsipur Assembly 291**. It retains the original Saarthi-logo loading animation and office password screen.

## Workflow (no Google Sheets)

- **Overview:** Gram Panchayat directory and consolidated counters.
- **Gram Panchayat Reports:** Select one GP, see a visual summary, and expand the **complete original responses to questions 1–12**, including tables and long Hindi text. Download the source DOCX.
- **Intelligence Lab:** Compare original responses to the same question across GPs and summarize documented issue categories. These are field reports, not representative surveys or vote predictions.
- **Issues Register:** Issue-by-issue cross-GP review with categories.
- **Add Reports:** Upload several DOCX files in the same 12-question format. Each new GP becomes one profile. Booth entries stay inside the original source question; there is no booth-wise dashboard.

## Report retention and confidentiality

**Uploaded DOCX files are in the browser's Streamlit session only** unless private storage is configured. A refresh/disconnect can clear them. The public dashboard repository contains **no actual report documents, personal contact details, or passwords**.

To retain reports permanently, create a **separate PRIVATE GitHub repository** for Word files. Configure its fine-grained repository token in **Streamlit Cloud → App settings → Secrets** (never commit it to GitHub):

```toml
dashboard_password = "YOUR_PRIVATE_OFFICE_PASSWORD"
report_store_repo = "OWNER/PRIVATE_REPORTS_REPO"
report_store_branch = "main"
report_store_token = "YOUR_FINE_GRAINED_TOKEN_WITH_CONTENTS_READ_WRITE"
```

The portal verifies that the configured report repository is private before reading or saving documents. DOCX files are stored in its `reports/` directory. Re-uploading the same GP updates the latest file while Git retains the version history. Without the optional storage credentials, the portal remains a functional session-only preview workspace.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Put your local password in `.streamlit/secrets.toml` or set `TULSIPUR_DASHBOARD_PASSWORD`. Do not commit real secrets. The application uses the code repository's `assets/saarthi-logo.png` for its splash and UI.

## Source verification

The parser flags disagreements between a GP's reported voter total and listed booth totals, and differences between current and historical booth IDs. It does **not** automatically equate the IDs. Q11 values are displayed as *field-recorded estimates*, not verified election support.

## Deployment

Streamlit Cloud should continue pointing to `app.py` in `nama2929/up-elections-tulsipur-ground-work-dashboard`. This feature branch can be reviewed in a pull request before merging into the deployed `main` branch.
