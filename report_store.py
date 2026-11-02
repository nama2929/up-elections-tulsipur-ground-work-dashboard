"""Optional private GitHub storage for confidential DOCX reports, separate from public app code."""
from __future__ import annotations
import base64
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from report_engine import parse_report

class ReportStore:
    def __init__(self, repo, token, branch="main"):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repo or ""):
            raise ValueError("Invalid report repository setting")
        if not token:raise ValueError("Private storage token missing")
        self.base="https://api.github.com/repos/"+repo
        self.token=token
        self.branch=branch
        self.verified=False

    def call(self,path,method="GET",body=None):
        data=json.dumps(body).encode() if body is not None else None
        request=urllib.request.Request(
            self.base+path,method=method,data=data,
            headers={"Authorization":"Bearer "+self.token,
                     "Accept":"application/vnd.github+json",
                     "X-GitHub-Api-Version":"2022-11-28",
                     "User-Agent":"Gram-Panchayat-Report-Viewer"})
        try:
            with urllib.request.urlopen(request,timeout=24) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as exc:
            if exc.code==404:raise FileNotFoundError("Private storage resource not found") from exc
            raise RuntimeError("Private storage failed (HTTP "+str(exc.code)+")") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError("Could not reach private report storage") from exc

    def ensure_private(self):
        if not self.verified:
            info=self.call("")
            if info.get("private") is not True:
                raise ValueError("Reports must be stored in a PRIVATE repository, never the public code repository")
            self.verified=True

    def list_reports(self):
        self.ensure_private()
        try:
            items=self.call("/contents/reports?"+urllib.parse.urlencode({"ref":self.branch}))
        except FileNotFoundError:return []
        result=[]
        if not isinstance(items,list):return result
        for f in items:
            if f.get("type")!="file" or not f.get("name","").lower().endswith(".docx"):
                continue
            if f.get("size",0)>8*1024*1024:continue
            path=urllib.parse.quote(f["path"],safe="/")
            item=self.call("/contents/"+path+"?"+urllib.parse.urlencode({"ref":self.branch}))
            if item.get("encoding")=="base64" and item.get("content"):
                raw=base64.b64decode(item["content"])
                result.append(parse_report(raw,f["name"]))
        return result

    def save(self,report):
        self.ensure_private()
        if len(report["raw"])>8*1024*1024:raise ValueError("Document exceeds 8 MB")
        name=re.sub(r"[^\\w-]+","_",report["name"],flags=re.UNICODE).strip("_")
        if not name:raise ValueError("Missing Gram Panchayat name")
        path="reports/"+name+".docx"
        api_path="/contents/"+urllib.parse.quote(path,safe="/")
        current_sha=None
        try:
            existing=self.call(api_path+"?"+urllib.parse.urlencode({"ref":self.branch}))
            current_sha=existing.get("sha")
        except FileNotFoundError:pass
        body={"message":"Update Gram Panchayat source document: "+name,
              "content":base64.b64encode(report["raw"]).decode(),
              "branch":self.branch}
        if current_sha:body["sha"]=current_sha
        self.call(api_path,"PUT",body)
        return bool(current_sha)
