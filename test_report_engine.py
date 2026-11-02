"""Synthetic tests for both the official Tulsipur DOCX and earlier report structure."""
from io import BytesIO
from docx import Document
from report_engine import parse_report, LABELS, display_question, aligned_sections

def table(doc,values):
    t=doc.add_table(rows=len(values),cols=len(values[0]))
    for ri,row in enumerate(values):
        for ci,value in enumerate(row):t.cell(ri,ci).text=str(value)

def build(legacy=False):
    doc=Document()
    old={
      1:"ग्राम पंचायत का विवरण",
      2:"ग्राम पंचायत में आने वाले बूथों का विवरण",
      3:"2022 में ग्राम पंचायत में आने वाले बूथों पर पड़े वोट",
      4:"ग्राम पंचायत की प्रमुख जातियां एवं राजनीतिक दलों के प्रति झुकाव",
      5:"ग्राम पंचायत की प्रमुख समस्याएं / स्थानीय मुद्दे",
      6:"वर्तमान समय में जेबा रिजवान जी की राजनीतिक एवं सामाजिक स्थिति",
      7:"वर्तमान में लोग युवा एवं पढ़े-लिखे चेहरे के रूप में किसे देखना पसंद कर रहे हैं?",
      8:"वर्तमान बीजेपी विधायक और विधानसभा स्तर के अन्य नेताओ की ग्राम पंचायत में स्थिति एवं जनाधार",
      9:"ग्राम पंचायत के प्रभावशाली एवं प्रमुख व्यक्तियों का विवरण",
      10:"ग्राम पंचायत का समग्र राजनीतिक विश्लेषण",
      11:"वर्तमान में प्रत्याशियों की स्थिति (प्रतिशत में)",
      12:"इस ग्राम पंचायत को जितने के लिए किसी नेता को क्या करना चाहिए सुझाव दें",
    }
    for q in range(1,13):
        doc.add_paragraph(f"{q}. "+(old[q] if legacy else LABELS[q]))
        if q==1:
            table(doc,[["ग्राम पंचायत का नाम","नमूना","ब्लॉक","टेस्ट"],["कुल मतदाताओं की संख्या","600","",""]])
        if q==(2 if legacy else 1):
            table(doc,[["बूथ नंबर","बूथ का नाम","कुल मतदाता"],["12","नमूना","580"]])
        if q==(3 if legacy else 2):
            table(doc,[["बूथ संख्या","बूथ का नाम","भाजपा वोट","सपा वोट"],["11","Sample","300","100"]])
        if q==(5 if legacy else 4):
            table(doc,[["मुद्दे","टिप्पणी / विवरण"],["खराब सड़क","सड़क की मरम्मत"]])
        if q==(11 if legacy else 12):
            table(doc,[["प्रत्याशी का नाम","समर्थन प्रतिशत (%)"],["विकल्प","50"]])
        if legacy and q==12:
            doc.add_paragraph("1. रिपोर्ट में दर्ज प्रथम टिप्पणी")
        if q==6:
            doc.add_paragraph("स्रोत से लिया गया नमूना पाठ।")
    out=BytesIO();doc.save(out)
    return parse_report(out.getvalue(),"synthetic.docx")

current=build()
assert current["format"]=="current"
assert current["name"]=="नमूना"
assert current["reported_voters"]==600
assert len(current["issues"])==1
assert current["votes"]["भाजपा वोट"]==300
assert current["estimates"]==[("विकल्प",50)]
assert len(current["headings"])==12
assert current["warnings"] and len(current["warnings"])==2
assert display_question(current,6).count("प्रश्न")==0
assert "समाजवादी पार्टी के प्रत्याशी" in display_question(current,6)
assert "युवा एवं पढ़े-लिखे" in display_question(current,11)
assert aligned_sections(current,1)==(1,)

legacy=build(True)
assert legacy["format"]=="legacy"
assert legacy["name"]=="नमूना"
assert len(legacy["issues"])==1
assert legacy["votes"]["भाजपा वोट"]==300
assert legacy["estimates"]==[("विकल्प",50)]
assert "ग्राम पंचायत में आने वाले बूथों" in display_question(legacy,2)
assert aligned_sections(legacy,1)==(1,2)
assert aligned_sections(legacy,12)==(11,)
assert legacy["sections"][12][-1][1].startswith("1.")
print("PASS: official questions, legacy source headings, charts, issue extraction, legacy crosswalk")
