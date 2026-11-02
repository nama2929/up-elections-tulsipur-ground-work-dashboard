"""Smoke-test both the password gate and the authenticated overview in Streamlit's test runner."""
from streamlit.testing.v1 import AppTest
app=AppTest.from_file("app.py",default_timeout=35)
app.run()
assert not app.exception, "Password gate crashed"
app.session_state["authenticated"]=True
app.run()
assert not app.exception, "Authenticated Gram Panchayat overview crashed"
print("PASS: existing password gate and new authenticated dashboard render")
