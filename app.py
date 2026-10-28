"""Saarthi Analytics | Tulsipur 291 Ground Operations Portal.

Standalone deployment shell modelled on the Manjhanpur operations dashboard.
Version 1: branded loading splash, password gate, empty reporting workspace.
There are deliberately NO Google Sheets, private data or mock field records.
"""
from __future__ import annotations

import base64
import datetime as dt
import hmac
import html
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from config import REPORT_SECTIONS, NAV_SECTIONS

ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "saarthi-logo.png"
LOGO_B64 = base64.b64encode(LOGO.read_bytes()).decode("ascii")
LOGO_URI = "data:image/png;base64," + LOGO_B64

st.set_page_config(
    page_title="Tulsipur | Saarthi Ground Operations",
    page_icon=str(LOGO),
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Saarthi Analytics • Tulsipur Ground Operations Portal"},
)
try:
    st.logo(str(LOGO), icon_image=str(LOGO), size="large")
except (AttributeError, TypeError):
    pass

# Keep credentials exclusively in Streamlit Cloud Secrets / environment variables.
# NEVER put an actual password in this file or commit secrets.toml to GitHub.
def configured_password() -> str:
    pw = os.environ.get("TULSIPUR_DASHBOARD_PASSWORD", "")
    if pw:
        return pw
    try:
        value = st.secrets.get("dashboard_password", "")
        return str(value) if value else ""
    except (FileNotFoundError, KeyError, AttributeError, OSError):
        return ""


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {--ink:#263747; --sub:#667582; --orange:#bc642f; --terracotta:#a95328; --cream:#fff7ed; --line:#e9e2d9; --paper:#fff; --bg:#faf8f5}
html, body, [data-testid="stApp"] {font-family:'Manrope','Hind',sans-serif!important; color:var(--ink)}
.stApp {background:var(--bg)!important}
.block-container {max-width:1300px;padding-top:1.1rem;padding-bottom:3.1rem}
#MainMenu, footer {visibility:hidden}
h1,h2,h3 {font-family:'Manrope','Hind',sans-serif!important;letter-spacing:-.035em!important;color:var(--ink)!important}
h1 {font-weight:800!important}
[data-testid="stSidebar"] {background:#fffaf5!important;border-right:1px solid var(--line)}
[data-testid="stSidebar"] [data-testid="stButton"] button {text-align:left!important}
[data-testid="stSidebar"] hr {border-color:var(--line)}
.stButton button, [data-testid="stFormSubmitButton"] button {min-height:43px!important;border-radius:11px!important;font-weight:700!important;border:1px solid #dec9b7!important;transition:all .12s ease;background:white;color:#824225}
.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover {border-color:var(--orange)!important;background:#fff2e9!important;color:#7b3e22!important}
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {background:var(--orange)!important;color:white!important;border:1px solid var(--orange)!important}
.stButton button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button[kind="primary"]:hover {background:#a64d22!important}
[data-testid="stTextInput"] input {border-radius:12px!important;min-height:48px!important;background:white!important;color:var(--ink)!important}
.brand {padding:14px 19px;background:white;border:1px solid #eadfd3;border-top:4px solid var(--orange);border-radius:19px;display:flex;align-items:center;justify-content:space-between;gap:16px;box-shadow:0 5px 25px rgba(40,35,26,.035);margin:0 0 13px}
.brand-left {display:flex;align-items:center;gap:14px;min-width:0}
.brand img {width:69px;height:69px;object-fit:contain;border-radius:50%}
.brand-name {font-size:1.22rem;font-weight:800;letter-spacing:-.045em;line-height:1.2}
.brand-kicker {font-size:.71rem;letter-spacing:.14em;color:#aa562a;font-weight:800;margin-top:5px}
.brand-status {color:#586b78;font-size:.78rem;text-align:right}
.brand-status strong {color:#b45a29;display:block;font-size:.85rem}
.hero {background:linear-gradient(113deg,white 2%,#fffaf5 60%,#f4e5d5);border:1px solid #eadccc;border-radius:21px;min-height:158px;padding:27px 29px;margin:12px 0 24px;position:relative;overflow:hidden}
.hero:before {content:"";position:absolute;width:320px;height:320px;border:1px solid rgba(188,100,47,.20);border-radius:50%;right:-85px;top:-196px}
.hero:after {content:"";position:absolute;width:230px;height:230px;border:1px solid rgba(188,100,47,.15);border-radius:50%;right:-50px;top:-113px}
.hero .eyebrow {color:#ad582b;letter-spacing:.17em;font-size:.73rem;font-weight:800;text-transform:uppercase;position:relative;z-index:1}
.hero h1 {font-size:clamp(1.75rem,3.2vw,2.55rem);margin:9px 0 8px;line-height:1.13;position:relative;z-index:1}
.hero .subtitle {font-size:.94rem;color:#5d6d79;margin:0;position:relative;z-index:1}
.section-title {font-size:1rem;letter-spacing:-.02em;font-weight:800;color:#314558;margin:15px 0 10px}
.metric-card {min-height:112px;border:1px solid #e7e0d8;background:#fff;border-radius:15px;padding:17px 18px;box-shadow:0 3px 15px rgba(36,35,29,.024);margin-bottom:8px}
.metric-cap {font-size:.78rem;color:#76818b;font-weight:650}
.metric-val {font-size:1.23rem;color:#273a4b;font-weight:800;margin:13px 0 4px;line-height:1.15}
.metric-foot {font-size:.72rem;color:#9a7463}
.empty-panel {border:1px dashed #d9beaa;background:linear-gradient(135deg,#fff,#fffaf5);border-radius:17px;text-align:center;padding:42px 18px 39px;margin:10px 0 18px}
.empty-icon {font-size:2.2rem;opacity:.85;margin-bottom:10px}
.empty-title {font-size:1.06rem;color:#2c4051;font-weight:800}
.empty-desc {max-width:610px;color:#71808b;font-size:.88rem;line-height:1.65;margin:9px auto 0}
.report-card {border:1px solid #e8e1d9;background:white;border-radius:14px;padding:18px 18px 14px;margin:4px 0;min-height:128px}
.report-icon {font-size:1.4rem;margin-bottom:8px}
.report-title {font-weight:800;color:#314353;font-size:.89rem}
.report-desc {font-size:.75rem;color:#788592;margin-top:6px;line-height:1.5}
.report-note {font-size:.74rem;color:#ac5c34;margin-top:8px;font-weight:700}
.side-kicker {font-size:.68rem;letter-spacing:.18em;font-weight:800;color:#b05c2b}
.side-title {font-size:1.05rem;color:#2b3c4e;font-weight:800;letter-spacing:-.02em}
.side-sub {color:#7a8791;font-size:.76rem;line-height:1.6}
.status-pill {display:inline-block;background:#fff0e4;color:#a75328;border:1px solid #efd5c2;font-weight:800;font-size:.73rem;letter-spacing:.02em;border-radius:100px;padding:6px 12px}
.footer-sa {display:flex;gap:9px;align-items:center;border-top:1px solid #eadfd4;padding:14px 0 0;color:#7b8894;font-size:.72rem;margin-top:27px}
.footer-sa img {width:34px;height:34px;border-radius:50%;object-fit:contain}
.footer-sa b {color:#394b5c}
.login-wrap {max-width:570px;margin:clamp(2vh,6vh,70px) auto 0;text-align:center}
.login-logo {width:135px;height:135px;border-radius:50%;object-fit:contain;margin-bottom:17px;filter:drop-shadow(0 9px 20px rgba(55,38,21,.10))}
.login-eyebrow {font-size:.73rem;letter-spacing:.20em;text-transform:uppercase;font-weight:800;color:#a45a31}
.login-title {font-size:clamp(1.8rem,3vw,2.5rem);letter-spacing:-.055em;font-weight:800;margin:10px 0 7px;color:#28394a}
.login-sub {font-size:.91rem;color:#74818b;line-height:1.7;max-width:500px;margin:auto}
.login-foot {text-align:center;font-size:.75rem;color:#98a1aa;padding-top:15px}
/* The splash is visually shown FIRST on each fresh browser session.
   No sensitive app content is sent until after password authentication. */
.sa-splash {position:fixed;inset:0;background:radial-gradient(circle at 50% 42%,#fffefc,#fff7ee 64%,#efdfce);display:flex;align-items:center;justify-content:center;z-index:999990;animation:saSplashHide 2.35s ease-in forwards}
.sa-splash-inner {width:min(410px,92vw);text-align:center;margin-top:-10px}
.sa-splash-logo {height:162px;width:162px;border-radius:50%;object-fit:contain;background:#fff;box-shadow:0 11px 55px rgba(86,60,37,.16);animation:saLogoIn .8s cubic-bezier(.2,.75,.2,1) both}
.sa-splash-name {font-size:1.27rem;font-weight:800;letter-spacing:.15em;color:#293a4b;margin-top:23px}
.sa-splash-sub {font-size:.78rem;letter-spacing:.1em;color:#bc642f;font-weight:800;margin-top:9px}
.sa-loader {height:4px;border-radius:8px;background:#eadacc;max-width:225px;overflow:hidden;margin:28px auto 0}
.sa-loader span {display:block;height:100%;width:0;background:#bd6330;border-radius:8px;animation:saLoading 1.75s ease-in-out .15s forwards}
.sa-splash-caption {font-size:.68rem;letter-spacing:.19em;text-transform:uppercase;color:#8b9aa2;margin-top:13px}
@keyframes saLoading {0%{width:0}55%{width:64%}100%{width:100%}}
@keyframes saLogoIn {from{transform:translateY(15px) scale(.93);opacity:0}to{transform:translateY(0) scale(1);opacity:1}}
@keyframes saSplashHide {0%,78%{opacity:1;visibility:visible}100%{opacity:0;visibility:hidden;pointer-events:none}}
@media(max-width:760px){.block-container{padding-left:1rem;padding-right:1rem;padding-top:.75rem}.brand{padding:11px;gap:8px}.brand img{width:53px;height:53px}.brand-name{font-size:.95rem}.brand-kicker{font-size:.55rem}.brand-status{display:none}.hero{padding:22px 17px;min-height:135px}.metric-card{min-height:98px}.login-wrap{margin-top:14px}}
@media(prefers-reduced-motion:reduce){.sa-splash {animation-duration:.3s}.sa-splash-logo,.sa-loader span{animation:none}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def splash_once() -> None:
    if st.session_state.get("splash_shown", False):
        return
    st.session_state.splash_shown = True
    st.markdown(
        f'<div class="sa-splash" role="status" aria-label="Loading Saarthi Analytics">'
        f'<div class="sa-splash-inner"><img class="sa-splash-logo" alt="Saarthi Analytics" src="{LOGO_URI}"/>'
        f'<div class="sa-splash-name">SAARTHI ANALYTICS</div>'
        f'<div class="sa-splash-sub">TULSIPUR • GROUND OPERATIONS</div>'
        f'<div class="sa-loader"><span></span></div>'
        f'<div class="sa-splash-caption">Preparing your workspace</div>'
        f'</div></div>', unsafe_allow_html=True,
    )


def gate() -> None:
    if st.session_state.get("authenticated", False):
        return

    # Keep the entire dashboard, its sidebar and its data out of the login route.
    st.markdown("<style>[data-testid='stSidebar']{display:none!important}</style>", unsafe_allow_html=True)
    splash_once()

    st.markdown(
        f'<div class="login-wrap"><img class="login-logo" src="{LOGO_URI}" alt="Saarthi Analytics logo">'
        f'<div class="login-eyebrow">SAARTHI ANALYTICS • PRIVATE WORKSPACE</div>'
        f'<div class="login-title">Tulsipur Ground Operations</div>'
        f'<p class="login-sub">Secure access to the Tulsipur Assembly 291 field operations portal. '
        f'Enter your office password to continue.</p></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    left, center, right = st.columns([1.1, 1, 1.1])
    with center:
        password = configured_password()
        if not password:
            st.warning("Office access is not configured yet. Set `dashboard_password` in Streamlit Secrets to enable sign-in.")

        with st.form("office_sign_in", clear_on_submit=False):
            supplied = st.text_input("Office password / कार्यालय पासवर्ड", type="password", placeholder="Enter office password")
            submitted = st.form_submit_button("Unlock portal  →", type="primary", use_container_width=True, disabled=not password)

        if submitted:
            if hmac.compare_digest(supplied.encode("utf-8"), password.encode("utf-8")):
                st.session_state.authenticated = True
                st.session_state.login_error = False
                st.rerun()
            else:
                st.session_state.login_error = True
        if st.session_state.get("login_error", False):
            st.error("Incorrect password. Please try again.")

    st.markdown('<div class="login-foot">Authorized Saarthi Analytics team members only · Tulsipur 291</div>', unsafe_allow_html=True)
    st.stop()


gate()

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "active_report" not in st.session_state:
    st.session_state.active_report = REPORT_SECTIONS[0][0]


def navigate(target: str) -> None:
    st.session_state.page = target


def select_report(code: str) -> None:
    st.session_state.active_report = code
    st.session_state.page = "Reports"


def section_title(name: str) -> None:
    st.markdown(f'<div class="section-title">{e(name)}</div>', unsafe_allow_html=True)


def empty_panel(title: str, description: str, icon: str = "▤") -> None:
    st.markdown(
        f'<div class="empty-panel"><div class="empty-icon">{e(icon)}</div>'
        f'<div class="empty-title">{e(title)}</div>'
        f'<p class="empty-desc">{e(description)}</p></div>', unsafe_allow_html=True,
    )


def card(title: str, value: str, foot: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-cap">{e(title)}</div>'
        f'<div class="metric-val">{e(value)}</div><div class="metric-foot">{e(foot)}</div></div>',
        unsafe_allow_html=True,
    )


def header() -> None:
    stamp = dt.datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y • %I:%M %p IST")
    st.markdown(
        f'<div class="brand"><div class="brand-left"><img src="{LOGO_URI}" alt="Saarthi Analytics logo"/>'
        f'<div><div class="brand-name">SAARTHI ANALYTICS</div>'
        f'<div class="brand-kicker">CONSTITUENCY INTELLIGENCE • TULSIPUR 291</div></div></div>'
        f'<div class="brand-status"><strong>Workspace ready</strong>{e(stamp)}</div></div>',
        unsafe_allow_html=True,
    )


def hero(title: str, sub: str, eyebrow: str = "TULSIPUR • ASSEMBLY 291") -> None:
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{e(eyebrow)}</div>'
        f'<h1>{e(title)}</h1><p class="subtitle">{e(sub)}</p></div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.image(str(LOGO), width=104)
    st.markdown('<div class="side-kicker">SAARTHI ANALYTICS</div><div class="side-title">Tulsipur 291</div>'
                '<div class="side-sub">Ground operations · Office view</div>', unsafe_allow_html=True)
    st.divider()
    st.caption("NAVIGATE / नेविगेट करें")
    for icon, destination in NAV_SECTIONS:
        st.button(f"{icon}  {destination}", key=f"sidebar_{destination}", use_container_width=True,
                  type="primary" if st.session_state.page == destination else "secondary",
                  on_click=navigate, args=(destination,))
    st.divider()
    st.markdown('<span class="status-pill">● No sheets connected</span>', unsafe_allow_html=True)
    st.caption("Data connections can be added in a future version. No field records are currently loaded.")
    st.write("")
    if st.button("Sign out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.login_error = False
        st.session_state.page = "Home"
        st.rerun()

header()

# Keep the same four top-level sections as the Manjhanpur portal.
st.caption("MAIN MENU / मुख्य मेन्यू")
for start in (0, 2):
    a, b = st.columns(2, gap="small")
    for col, (icon, destination) in zip((a, b), NAV_SECTIONS[start:start + 2]):
        with col:
            st.button(f"{icon}  {destination}", key=f"top_{destination}", use_container_width=True,
                      type="primary" if st.session_state.page == destination else "secondary",
                      on_click=navigate, args=(destination,))

page = st.session_state.page
if page == "Home":
    hero("Ground Operations Dashboard", "Tulsipur Assembly 291 · Saarthi Analytics field monitoring workspace")
    st.markdown('<span class="status-pill">SETUP MODE · DATA CONNECTIONS PENDING</span>', unsafe_allow_html=True)
    section_title("Workspace at a glance")
    a, b, c, d = st.columns(4, gap="small")
    with a: card("Reporting records", "Not connected", "No reporting sheet added")
    with b: card("Coordinators", "Not configured", "Team list pending")
    with c: card("Booth visits", "—", "Awaiting field reports")
    with d: card("Last data sync", "—", "No source configured")
    section_title("Recent field activity")
    empty_panel("Awaiting the first data connection",
                "This portal is ready for Tulsipur. When your team sheets are connected, verified field updates, daily activity and coordinator reports can appear here.", "📋")
    section_title("Explore reporting sections")
    for i in range(0, len(REPORT_SECTIONS), 3):
        cols = st.columns(3, gap="small")
        for col, (code, icon, name, desc) in zip(cols, REPORT_SECTIONS[i:i + 3]):
            with col:
                st.markdown(f'<div class="report-card"><div class="report-icon">{e(icon)}</div>'
                            f'<div class="report-title">{e(name)}</div><div class="report-desc">{e(desc)}</div></div>',
                            unsafe_allow_html=True)
                st.button(f"Open {name}", key=f"home_{code}", on_click=select_report,
                          args=(code,), use_container_width=True)

elif page == "Reports":
    hero("Field Reporting", "Field reporting categories prepared for Tulsipur — no source sheets linked yet.")
    section_title("Choose a reporting section / रिपोर्ट चुनें")
    for i in range(0, len(REPORT_SECTIONS), 2):
        cols = st.columns(2, gap="small")
        for col, (code, icon, name, desc) in zip(cols, REPORT_SECTIONS[i:i + 2]):
            with col:
                st.button(f"{icon}  {name}", key=f"select_{code}",
                          type="primary" if st.session_state.active_report == code else "secondary",
                          use_container_width=True, on_click=select_report, args=(code,))
    selected = next(s for s in REPORT_SECTIONS if s[0] == st.session_state.active_report)
    section_title(selected[2])
    empty_panel("No records available yet",
                f"The {selected[2].lower()} section is ready. No Google Sheet is attached, so no totals, charts or field entries are shown.", selected[1])

elif page == "Daily Summary":
    hero("Daily Summary", "A daily view of field execution, ready to populate when verified reports are connected.")
    section_title("Reporting timeline")
    empty_panel("No dated field reports",
                "Daily trends, latest submissions and day-wise summaries will be available after the first Tulsipur reporting source is connected.", "📅")

elif page == "Team":
    hero("Coordinator Overview", "Team-level reporting for Tulsipur Assembly 291.")
    section_title("Team activity")
    empty_panel("Coordinator roster is not configured",
                "Coordinator names, assignments and reporting summaries will appear here after the Tulsipur team and its reporting sheets are added.", "👥")

st.markdown(
    f'<div class="footer-sa"><img src="{LOGO_URI}" alt="Saarthi Analytics"/>'
    f'<div><b>Saarthi Analytics</b> · Tulsipur Ground Operations Portal<br/>'
    f'Password-protected workspace · Reporting integrations not yet connected</div></div>',
    unsafe_allow_html=True,
)
