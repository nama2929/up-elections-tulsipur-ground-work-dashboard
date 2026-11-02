"""Synthetic tests with no personal or political field data."""
from io import BytesIO
from docx import Document
from report_engine import parse_report, LABELS

doc=Document()
for q,label in LABELS.items():
    doc.add_paragraph(f"{q}. {label}")
    if q==1:
        tbl=doc.add_table(rows=2,cols=4)
        for i,value in enumerate(["ग्राम पंचायत का नाम","नमूना","ब्लॉक","नमूना ब्लॉक"]):
            tbl.cell(0,i).text=value
        for i,value in enumerate(["कुल मतदाताओं की संख्या","600","",""]):
            tbl.cell(1,i).text=value
    elif q==2:
        tbl=doc.add_table(rows=2,cols=3)
        for i,v in enumerate(["बूथ नंबर","बूथ नाम","कुल मतदाता"]):tbl.cell(0,i).text=v
        for i,v in enumerate(["12","नमूना","580"]):tbl.cell(1,i).text=v
    elif q==3:
        tbl=doc.add_table(rows=2,cols=3)
        for i,v in enumerate(["बूथ संख्या","बूथ का नाम","कुल वोट"]):tbl.cell(0,i).text=v
        for i,v in enumerate(["11","Sample","400"]):tbl.cell(1,i).text=v
    elif q==5:
        tbl=doc.add_table(rows=2,cols=2)
        for i,v in enumerate(["मुद्दे","विवरण"]):tbl.cell(0,i).text=v
        for i,v in enumerate(["खराब सड़क","गाँव में सड़क की मरम्मत आवश्यक"]):tbl.cell(1,i).text=v
    elif q==11:
        tbl=doc.add_table(rows=2,cols=2)
        for i,v in enumerate(["विवरण","प्रतिशत"]):tbl.cell(0,i).text=v
        for i,v in enumerate(["विकल्प","50"]):tbl.cell(1,i).text=v
    elif q==12:
        tbl=doc.add_table(rows=1,cols=1)
        tbl.cell(0,0).text="1. स्रोत के अनुसार दर्ज जानकारी"
    else:
        doc.add_paragraph("Example response for validation.")
buf=BytesIO()
doc.save(buf)
report=parse_report(buf.getvalue(),"sample.docx")
assert report["name"]=="नमूना", report["name"]
assert len(report["sections"])==12
assert all(report["sections"][i] for i in LABELS)
assert report["issues"] and len(report["issues"])==1
assert report["votes"]["कुल वोट"]==400
assert report["reported_voters"]==600
assert len(report["warnings"])==2
assert report["sections"][12][0][1][0][0].startswith("1.")
print("PASS: GP metadata, 12 original questions, tables, totals, issues, source checks")
