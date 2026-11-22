"""Smoke test for the user-facing Streamlit application."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]

def run():
    app=AppTest.from_file(str(ROOT/"app.py"),default_timeout=90).run()
    if app.exception:
        raise AssertionError([str(x.message) for x in app.exception])
    if "Inteligencia de demanda y pronósticos" not in [x.value for x in app.title]:
        raise AssertionError("Spanish dashboard title not found")
    print("PASS: Spanish dashboard, loaded outputs")
    languages=[x for x in app.sidebar.radio if x.label=="Idioma / Language"]
    if len(languages)!=1: raise AssertionError("Language selector missing")
    languages[0].set_value("English").run()
    if app.exception:
        raise AssertionError([str(x.message) for x in app.exception])
    if "Demand Intelligence & Forecasting" not in [x.value for x in app.title]:
        raise AssertionError("English dashboard title not found")
    print("PASS: English dashboard")

if __name__=="__main__":
    run()
