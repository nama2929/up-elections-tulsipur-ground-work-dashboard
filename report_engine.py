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
 1:"ग्राम पंचायत का विवरण", 2:"ग्राम पंचायत के बूथों का विवरण",
 3:"2022 के दर्ज चुनावी आंकड़े", 4:"स्थानीय सामाजिक विवरण",
 5:"प्रमुख समस्याएँ / स्थानीय मुद्दे", 6:"प्रश्न 6 · मूल टिप्पणी",
 7:"प्रश्न 7 · मूल टिप्पणी", 8:"प्रश्न 8 · मूल टिप्पणी",
 9:"प्रमुख व्यक्तियों का विवरण", 10:"समग्र विश्लेषण",
 11:"रिपोर्ट में दर्ज अनुमान", 12:"सुझाव · मूल उत्तर",
}
QHEADING = re.compile(r"^\s*(1[0-2]|[1-9])\s*[.．।:]\s*(.+)")
def clean(x): return re.sub(r"\s+"," ",str(x or "")).strip()
def to_int(x):
    value=re.sub(r"[^0-9]","",str(x or "").translate(str.maketrans("०१२३४५६७८९","0123456789")))
    return int(value) if value else 0

def parse_report(data, filename):
    doc=Document(BytesIO(data))
    sections={i:[] for i in LABELS}
    section=None
    for part in doc.element.body:
        if part.tag.endswith("}p"):
            raw=Paragraph(part,doc).text.strip()
            match=QHEADING.match(clean(raw))
            if match and not (section==12 and int(match.group(1))<12):
                new=int(match.group(1))
                # In the main report numbered headings have meaningful title text.
                if len(match.group(2).strip())>=8:
                    section=new
                    continue
            if raw and section: sections[section].append(("paragraph",raw))
        elif part.tag.endswith("}tbl") and section:
            table=Table(part,doc)
            sections[section].append(("table",[[cell.text.strip() for cell in row.cells] for row in table.rows]))
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
    for row in rows(5)[1:]:
        if len(row)>1 and clean(row[0]):issues.append((clean(row[0]),clean(" ".join(row[1:]))))
    votes={}
    his=rows(3)
    for i,h in enumerate(his[0] if his else []):
        if i>=2 and clean(h):
            votes[clean(h)]=sum(to_int(r[i]) for r in his[1:] if len(r)>i)
    estimates=[]
    for row in rows(11)[1:]:
        if len(row)>1 and clean(row[0]):
            estimates.append((clean(row[0]),to_int(row[-1])))
    warnings=[]
    current=rows(2)
    current_total=sum(to_int(row[2]) for row in current[1:] if len(row)>2)
    reported=to_int(field("कुल मतदाताओं"))
    if current_total and reported and current_total!=reported:
        warnings.append(f"Reported voters {reported:,}; listed booth total {current_total:,}. Please verify.")
    if {clean(r[0]) for r in current[1:] if r}!={clean(r[0]) for r in his[1:] if r}:
        warnings.append("Current booth IDs and historical IDs differ; no automatic mapping performed.")
    return dict(name=name,block=field("ब्लॉक") or "—",reported_voters=reported,
      issues=issues,sections=sections,votes=votes,estimates=estimates,warnings=warnings,
      filename=filename,raw=data,digest=hashlib.sha256(data).hexdigest())
