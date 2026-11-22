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
    expected={"WAPE base","WAPE SES","WAPE ABC/XYZ","Mejora vs. base"}
    labels={x.label for x in app.metric}
    if not expected.issubset(labels):
        raise AssertionError(f"Spanish KPI labels missing: {expected-labels}")
    if not any(x.label=="Método de la matriz" for x in app.selectbox):
        raise AssertionError("ABC/XYZ segment matrix selector missing")
    if not any(x.label=="Mostrar productos" for x in app.selectbox):
        raise AssertionError("Review list size selector missing")
    print("PASS: Spanish dashboard, segment matrix and concise KPI labels")
    languages=[x for x in app.sidebar.radio if x.label=="Idioma / Language"]
    if len(languages)!=1: raise AssertionError("Language selector missing")
    languages[0].set_value("English").run()
    if app.exception:
        raise AssertionError([str(x.message) for x in app.exception])
    if "Demand Intelligence & Forecasting" not in [x.value for x in app.title]:
        raise AssertionError("English dashboard title not found")
    en_expected={"Baseline WAPE","WAPE SES","WAPE ABC/XYZ","Gain vs. baseline"}
    en_labels={x.label for x in app.metric}
    if not en_expected.issubset(en_labels):
        raise AssertionError(f"English KPI labels missing: {en_expected-en_labels}")
    print("PASS: English dashboard, terminology and metrics")

if __name__=="__main__":
    run()
