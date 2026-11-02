"""Structured DOCX reader for 12-question Gram Panchayat reports; no external data connections."""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import hashlib
import re
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

LABELS = {
 1:"ग्राम पंचायत का नाम एवं उसमें आने वाले बूथों का विवरण",
 2:"2022 में ग्राम पंचायत में आने वाले बूथों पर पड़े वोट",
 3:"ग्राम पंचायत की प्रमुख जातियां एवं राजनीतिक दलों के प्रति सामाजिक झुकाव",
 4:"ग्राम पंचायत की प्रमुख समस्याएं एवं स्थानीय मुद्दे",
 5:"वर्तमान समय में जेबा रिजवान जी की राजनीतिक एवं सामाजिक स्थिति",
 6:"समाजवादी पार्टी के प्रत्याशी के रूप में जेबा रिजवान जी की स्थिति",
 7:"निर्दलीय उम्मीदवार के रूप में जेबा रिजवान जी की स्थिति",
 8:"वर्तमान विधायक की ग्राम पंचायत में स्थिति एवं जनाधार",
 9:"ग्राम पंचायत के प्रभावशाली एवं प्रमुख व्यक्तियों का विवरण",
 10:"ग्राम पंचायत का समग्र राजनीतिक विश्लेषण",
 11:"वर्तमान में लोग युवा एवं पढ़े-लिखे चेहरे के रूप में किसे देखना पसंद कर रहे हैं?",
 12:"वर्तमान में प्रत्याशियों की स्थिति (प्रतिशत में)",
}
LEGACY_CROSSWALK = {1:(1,2),2:(3,),3:(4,),4:(5,),5:(6,),6:(6,),7:(6,),8:(8,),9:(9,),10:(10,),11:(7,),12:(11,)}
QHEADING = re.compile(r"^\s*(?:प्रश्न\s*)?(1[0-2]|[1-9])\s*[.．।:)\-–]\s*(.+)")
def clean(x): return re.sub(r"\s+"," ",str(x or "")).strip()
def to_int(x):
    value=re.sub(r"[^0-9]","",str(x or "").translate(str.maketrans("०१२३४५६७८९","0123456789")))
    return int(value) if value else 0


def display_question(report,q):
    """One number and the exact original heading, never duplicate 'प्रश्न'."""
    heading=report.get("headings",{}).get(q) or LABELS[q]
    heading=re.sub(r"^\s*(?:प्रश्न\s*)?(?:1[0-2]|[1-9])\s*[.．।:)\-–]\s*","",heading)
    heading=re.sub(r"^प्रश्न\s*(?:1[0-2]|[1-9])\s*[:.\-–]*\s*","",heading)
    return f"{q:02d} · {heading}"

def aligned_sections(report,official_question):
    """Crosswalk only for comparing reports with older question ordering."""
    return LEGACY_CROSSWALK[official_question] if report.get("format")=="legacy" else (official_question,)

def parse_report(data, filename):
    doc=Document(BytesIO(data))
    sections={i:[] for i in LABELS}
    headings={}
    section=None
    for part in doc.element.body:
        if part.tag.endswith("}p"):
            raw=Paragraph(part,doc).text.strip()
            match=QHEADING.match(clean(raw))
            if match and int(match.group(1))==(section or 0)+1:
                section=int(match.group(1))
                headings[section]=clean(match.group(2))
                continue
            if raw and section: sections[section].append(("paragraph",raw))
        elif part.tag.endswith("}tbl") and section:
            table=Table(part,doc)
            sections[section].append(("table",[[cell.text.strip() for cell in row.cells] for row in table.rows]))
    fmt="current" if "बूथ" in headings.get(1,"") and "2022" in headings.get(2,"") else "legacy"
    def rows(q):
        return [r for kind,table in sections[q] if kind=="table" for r in table if any(clean(c) for c in r)]
    fields={}
    for row in rows(1):
        for i in (0,2):
            if len(row)>i+1 and clean(row[i]):
                fields[clean(row[i])]=clean(row[i+1])
    def field(t):
        return next((v for k,v in fields.items() if t in k),"")
    name=field("ग्राम पंचायत का नाम") or Path(filename).stem.replace(" ग्राम पंचायत रिपोर्ट","")
    issues=[]
    for row in rows(4 if fmt=="current" else 5)[1:]:
        if len(row)>1 and clean(row[0]):issues.append((clean(row[0]),clean(" ".join(row[1:]))))
    votes={}
    his=rows(2 if fmt=="current" else 3)
    for i,h in enumerate(his[0] if his else []):
        if i>=2 and clean(h):
            votes[clean(h)]=sum(to_int(r[i]) for r in his[1:] if len(r)>i)
    estimates=[]
    for row in rows(12 if fmt=="current" else 11)[1:]:
        if len(row)>1 and clean(row[0]):
            estimates.append((clean(row[0]),to_int(row[-1])))
    warnings=[]
    current=([r for kind,t in sections[1] if kind=="table" and t and "बूथ नंबर" in clean(" ".join(t[0])) for r in t if any(clean(c) for c in r)] if fmt=="current" else rows(2))
    current_total=sum(to_int(row[2]) for row in current[1:] if len(row)>2)
    reported=to_int(field("कुल मतदाताओं"))
    if current_total and reported and current_total!=reported:
        warnings.append(f"Reported voters {reported:,}; listed booth total {current_total:,}. Please verify.")
    if {clean(r[0]) for r in current[1:] if r}!={clean(r[0]) for r in his[1:] if r}:
        warnings.append("Current booth IDs and historical IDs differ; no automatic mapping performed.")
    return dict(name=name,block=field("ब्लॉक") or "—",reported_voters=reported,
      issues=issues,sections=sections,headings=headings,format=fmt,votes=votes,estimates=estimates,warnings=warnings,
      filename=filename,raw=data,digest=hashlib.sha256(data).hexdigest())
