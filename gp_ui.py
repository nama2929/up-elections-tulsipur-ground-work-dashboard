"""Tulsipur Gram Panchayat workspace. Runs only after the existing portal password gate."""
import html
from collections import Counter
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from report_engine import LABELS, parse_report
from report_store import ReportStore

ROOT=Path(__file__).resolve().parent
PAGES=["Overview","Gram Panchayat Reports","Intelligence Lab","Issues Register","Add Reports"]
TOPICS={
 "सड़क / Roads":("सड़क","जर्जर","कच्ची सड़क","मार्ग","पुल"),
 "स्वच्छता / Sanitation":("गंदगी","कचरा","सफाई","नाली"),
 "पानी / Water":("पानी","जल","सिंचाई"),
 "बिजली / Electricity":("बिजली","ट्रांसफार्मर"),
 "सामुदायिक सुविधाएँ":("विवाह भवन","सामुदायिक","भवन"),
 "स्वास्थ्य / Health":("स्वास्थ्य","बीमारी","अस्पताल"),
 "शिक्षा / Education":("शिक्षा","स्कूल","विद्यालय"),
}
def safe(x):return html.escape(str(x),quote=True)

def secrets(key):
    try:return str(st.secrets.get(key,"") or "")
    except Exception:return ""

@st.cache_data(ttl=90,show_spinner=False)
def private_reports(repo,branch,token):
    return ReportStore(repo,token,branch).list_reports()

def chart(items, unit=""):
    if not items:return st.caption("No data entered for this chart.")
    fig=go.Figure(go.Bar(
        x=[v for k,v in items],y=[k for k,v in items],orientation="h",
        marker_color="#b76945",text=[str(v)+unit for k,v in items],
        textposition="outside",cliponaxis=False))
    fig.update_layout(
        height=max(260,60*len(items)+90),
        margin=dict(l=20,r=55,t=20,b=20),
        paper_bgcolor="#fff",plot_bgcolor="#fff",
        font=dict(family="Arial",color="#304353"),
        yaxis=dict(autorange="reversed"),showlegend=False)
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

def raw_blocks(report,q):
    blocks=report["sections"].get(q,[])
    if not blocks:
        st.caption("No response in source report.")
        return
    for kind,val in blocks:
        if kind=="paragraph":
            st.write(val)
            continue
        if not val:continue
        if len(val[0])==1:
            for row in val:
                for cell in row:
                    if cell.strip():st.markdown(cell.replace("\n","\n\n"))
            continue
        if q==6 and len(val[0])==2:
            cols=st.columns(2)
            for i,col in enumerate(cols):
                with col:
                    st.markdown("**"+safe(val[0][i])+"**",unsafe_allow_html=True)
                    for row in val[1:]:
                        if len(row)>i:st.write(row[i])
            continue
        heads=[(c.strip() or f"Column {i+1}")+f" · {i+1}" for i,c in enumerate(val[0])]
        records=[{heads[i]:(row[i] if i<len(row) else "") for i in range(len(heads))}
                 for row in val[1:] if any(c.strip() for c in row)]
        if records:st.dataframe(pd.DataFrame(records),hide_index=True,use_container_width=True)
        else:
            for row in val:
                st.write(" | ".join(c for c in row if c.strip()))

def find_q(q,repo):
    for kind,value in repo["sections"].get(q,[]):
        if kind=="table":return value
    return []

def issue_topics(title,details):
    combined=title+" "+details
    return [name for name,words in TOPICS.items() if any(w in combined for w in words)] or ["Other"]

def report_page(report):
    st.markdown("### "+safe(report["name"]),unsafe_allow_html=True)
    st.caption("Block / ब्लॉक: "+report["block"]+" · Original 12-question field report")
    a,b,c=st.columns(3)
    a.metric("Reported voters",f'{report["reported_voters"]:,}' if report["reported_voters"] else "—")
    b.metric("Local issues",len(report["issues"]))
    c.metric("Questions found",sum(bool(report["sections"][i]) for i in LABELS))
    visual,original,checks=st.tabs(["Visual overview","Original report · 12 questions","Source verification"])
    with visual:
        st.markdown("#### Reported local issues")
        for title,details in report["issues"]:
            with st.container(border=True):
                st.markdown("**"+safe(title)+"**",unsafe_allow_html=True)
                st.write(details)
        if not report["issues"]:st.caption("No issues have been entered.")
        st.divider()
        x,y=st.columns(2)
        with x:
            st.markdown("#### Historical totals")
            st.caption("Q3 · Vote entries summed within this Gram Panchayat only; historical booth IDs are not mapped to current booths.")
            chart(list(report["votes"].items()))
        with y:
            st.markdown("#### Field-recorded percentage estimates")
            st.caption("Q11 · Report author's estimates; these are NOT representative polling or validated voter support.")
            chart(report["estimates"],"%")
        st.markdown("#### Source narrative · Q10")
        raw_blocks(report,10)
    with original:
        st.info("Every question retains the original Hindi response, including complete tables and long-form notes.")
        for q,label in LABELS.items():
            with st.expander(f"प्रश्न {q:02} — {label}",expanded=q==1):
                raw_blocks(report,q)
        st.download_button("Download original Word report",report["raw"],
          file_name=report["filename"],mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          key="dl_"+report["digest"][:12])
    with checks:
        if report["warnings"]:
            for warning in report["warnings"]:st.warning(warning)
        else:st.info("No automated discrepancy detected; manual source verification is still recommended.")
        st.caption("Source: "+report["filename"]+" · SHA-256: "+report["digest"][:16]+"…")
        st.caption("The Word document is the source of record.")

def run():
    if not st.session_state.get("authenticated",False):
        st.stop()
    st.markdown("""
    <style>
    .stApp{background:#faf9f7}
    [data-testid="stSidebar"]{background:#fffdfa!important}
    [data-testid="stMetric"]{background:white;padding:16px;border:1px solid #eee7df;border-radius:16px}
    [data-testid="stExpander"]{background:white;border:1px solid #eee7df;border-radius:12px;margin:5px 0}
    .gp-hero{background:linear-gradient(120deg,#ffffff,#fff1e4);
      border:1px solid #eadfd2;border-radius:20px;padding:25px;margin:8px 0 22px}
    .gp-hero h1{margin:4px 0 8px;letter-spacing:-.04em;color:#273846}
    .gp-hero p{color:#687987;margin:0}
    </style>
    """,unsafe_allow_html=True)
    if "reports_session" not in st.session_state:st.session_state.reports_session={}
    if "gp_section" not in st.session_state:st.session_state.gp_section="Overview"
    if "gp_current" not in st.session_state:st.session_state.gp_current=""
    store=None;storage_error=""
    repo=secrets("report_store_repo");token=secrets("report_store_token")
    branch=secrets("report_store_branch") or "main"
    persisted=[]
    if repo and token:
        try:
            store=ReportStore(repo,token,branch)
            persisted=private_reports(repo,branch,token)
        except Exception as exc:
            storage_error="Private report repository unavailable: "+str(exc)
            store=None
    reports={r["name"]:r for r in persisted}
    reports.update(st.session_state.reports_session)
    with st.sidebar:
        st.image(str(ROOT/"assets"/"saarthi-logo.png"),width=90)
        st.markdown("**SAARTHI ANALYTICS**")
        st.caption("Tulsipur · Assembly 291")
        st.divider()
        for page in PAGES:
            if st.button(page,use_container_width=True,key="gp_"+page,
              type="primary" if page==st.session_state.gp_section else "secondary"):
                st.session_state.gp_section=page
                st.rerun()
        st.divider()
        st.caption(f'{len(reports)} Gram Panchayat report(s)')
        st.caption("Data source: Word reports · No Google Sheets")
        if store:st.caption("Private report storage connected")
        elif storage_error:st.warning(storage_error)
        else:st.caption("Preview mode · uploads only last this browser session")
        if st.button("Sign out",use_container_width=True):
            st.session_state.authenticated=False
            st.session_state.reports_session={}
            st.session_state.gp_section="Overview"
            st.rerun()
    page=st.session_state.gp_section
    st.markdown(f'<div class="gp-hero"><div style="font-size:11px;letter-spacing:.13em;color:#a65b30;font-weight:800">SAARTHI · TULSIPUR 291</div><h1>{safe(page)}</h1><p>Gram Panchayat-wise reporting and source-verified field observations.</p></div>',
                unsafe_allow_html=True)
    if page=="Overview":
        a,b,c=st.columns(3)
        a.metric("Gram Panchayats",len(reports))
        b.metric("Reported voters",f'{sum(r["reported_voters"] for r in reports.values()):,}' if reports else "—")
        c.metric("Documented issues",sum(len(r["issues"]) for r in reports.values()))
        st.markdown("#### Gram Panchayat directory")
        search=st.text_input("Search Gram Panchayat or block",placeholder="Search name / block...")
        for name,r in sorted(reports.items()):
            if search and search.lower() not in (name+" "+r["block"]).lower():continue
            with st.container(border=True):
                left,right=st.columns([4,1],vertical_alignment="center")
                with left:
                    st.markdown("**"+safe(name)+"** · "+safe(r["block"]),unsafe_allow_html=True)
                    st.caption(f'{len(r["issues"])} issues · 12-question source')
                with right:
                    if st.button("Open report",key="open_"+r["digest"][:12],use_container_width=True):
                        st.session_state.gp_current=name
                        st.session_state.gp_section="Gram Panchayat Reports"
                        st.rerun()
        if not reports:st.info("No Word reports have been saved yet. Use Add Reports to upload the first DOCX.")
    elif page=="Gram Panchayat Reports":
        if not reports:st.info("Upload a report to see its visual profile and all 12 original answers.")
        else:
            names=sorted(reports)
            chosen=st.session_state.gp_current
            index=names.index(chosen) if chosen in names else 0
            name=st.selectbox("Select Gram Panchayat / ग्राम पंचायत चुनें",names,index=index)
            st.session_state.gp_current=name
            report_page(reports[name])
    elif page=="Intelligence Lab":
        st.caption("Research comparison only. No automatic voter-sentiment claims, targeting or electoral prediction.")
        if not reports:st.info("Upload reports to enable cross-Panchayat comparison.")
        else:
            q=st.selectbox("Compare original question across Gram Panchayats",list(LABELS),
                           format_func=lambda x:f"Q{x:02} — {LABELS[x]}")
            for name,r in sorted(reports.items()):
                with st.expander(name+" · "+r["block"],expanded=len(reports)==1):
                    raw_blocks(r,q)
            st.divider()
            counts=Counter(t for r in reports.values() for title,desc in r["issues"] for t in set(issue_topics(title,desc)))
            st.markdown("#### Recurring documented issue categories")
            chart(counts.most_common())
            st.caption("Counts refer to report entries, not population prevalence.")
    elif page=="Issues Register":
        rows=[]
        for r in reports.values():
            for title,desc in r["issues"]:
                rows.append({"ग्राम पंचायत":r["name"],"ब्लॉक":r["block"],"मुद्दा":title,
                             "विवरण":desc,"श्रेणी":", ".join(issue_topics(title,desc))})
        if rows:
            categories=["All categories"]+sorted(set(t for r in rows for t in r["श्रेणी"].split(", ")))
            selected=st.selectbox("Filter issue category",categories)
            filtered=rows if selected=="All categories" else [r for r in rows if selected in r["श्रेणी"]]
            st.dataframe(pd.DataFrame(filtered),hide_index=True,use_container_width=True)
        else:st.info("No issues reported yet.")
    elif page=="Add Reports":
        st.markdown("#### Upload Word reports")
        uploaded=st.file_uploader("Select Gram Panchayat DOCX files",type=["docx"],accept_multiple_files=True)
        if uploaded:
            for f in uploaded:
                try:
                    if f.size>8*1024*1024:raise ValueError("File over 8 MB limit")
                    r=parse_report(f.getvalue(),f.name)
                    st.session_state.reports_session[r["name"]]=r
                    st.success(r["name"]+f' · {sum(bool(r["sections"][q]) for q in LABELS)}/12 questions detected')
                    for warning in r["warnings"]:st.warning(warning)
                except Exception as exc:st.error(f.name+": "+str(exc))
        st.markdown("#### Save new reports permanently")
        if storage_error:st.error(storage_error)
        elif not store:
            st.warning("Preview only: documents are held in this browser session. Set up a separate PRIVATE report repository via Streamlit Secrets to keep them available to your team.")
            st.caption("Required secrets: report_store_repo, report_store_token, report_store_branch (optional). Never commit personal reports to the public dashboard repo.")
        else:
            selected=st.multiselect("Choose reports to save",sorted(st.session_state.reports_session),
                                    default=sorted(st.session_state.reports_session))
            approved=st.checkbox("I reviewed these reports and confirm that updating an existing Gram Panchayat will replace its current document (Git keeps revision history).")
            if st.button("Save to private report repository",type="primary",disabled=not selected or not approved):
                for name in selected:
                    try:
                        updated=store.save(st.session_state.reports_session[name])
                        st.success(name+(" updated in private storage" if updated else " saved to private storage"))
                    except Exception as exc:st.error(name+": "+str(exc))
                private_reports.clear()
        st.caption("Expected document format: 12 numbered questions, with Q1 naming the Gram Panchayat and Q5 listing local issues.")
