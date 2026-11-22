"""Bilingual Streamlit dashboard for the UCI weekly forecasting case."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"
NEEDED=[
    "model_summary.csv","final_predictions.csv","decision_exceptions.csv",
    "portfolio_profile.csv","policy_overall_metrics.csv",
    "policy_horizon_metrics.csv","prospective_review_queue.csv"
]
st.set_page_config(page_title="Demand Intelligence | CS Intelligence",page_icon="📈",layout="wide")
lang=st.sidebar.radio("Idioma / Language",["Español","English"],horizontal=True)

def T(es,en):
    return es if lang=="Español" else en

st.title(T("Inteligencia de demanda y pronósticos","Demand Intelligence & Forecasting"))
st.caption(T(
    "CS Intelligence | 811 productos, 52 semanas indexadas | Datos públicos de UCI",
    "CS Intelligence | 811 products, 52 indexed weeks | Public UCI data"
))
st.markdown(T(
    "¿Cuánta complejidad hace falta para pronosticar cantidades y decidir qué productos revisar?",
    "How much forecasting complexity is needed to predict quantities and decide which products to review?"
))

missing=[name for name in NEEDED if not (OUT/name).exists()]
if missing:
    st.error(T(
        "Faltan resultados del análisis. Primero ejecuta el procedimiento de reproducción documentado.",
        "Analysis outputs are missing. Run the documented reproduction steps first."
    ))
    st.code("python reproduce.py",language="bash")
    st.write(", ".join(missing))
    st.stop()

@st.cache_data(show_spinner=False)
def load(name):
    return pd.read_csv(OUT/name)

summary=load("model_summary.csv")
policy=load("policy_overall_metrics.csv")
pred=load("final_predictions.csv")
profile=load("portfolio_profile.csv")
horizons=load("policy_horizon_metrics.csv")
queue=load("prospective_review_queue.csv")
exceptions=load("decision_exceptions.csv")

vals=policy.set_index("strategy")
naive=float(vals.loc["naive","wape"])
ses=float(vals.loc["ses","wape"])
seg=float(vals.loc["segmented_policy","wape"])
reduction=1-float(vals.loc["ses","absolute_error"])/float(vals.loc["naive","absolute_error"])

labels={
    "naive":T("Referencia: último valor observado","Naive benchmark: last observed value"),
    "ses":T("Suavizamiento exponencial simple (SES)","Simple exponential smoothing (SES)"),
    "segmented_policy":T("Selección por segmentos ABC/XYZ","ABC/XYZ segment-based selection")
}
tiers={
    "High":T("Alta","High"),
    "Medium":T("Media","Medium"),
    "Routine":T("Rutinaria","Routine")
}
reason_es={
    "high historical volume":"alto volumen histórico",
    "volatile observed quantities":"cantidades observadas volátiles",
    "many zero weeks":"muchas semanas con cero compras",
    "recent four-week shift":"cambio reciente en cuatro semanas",
    "routine review":"revisión ordinaria"
}
actions_es={
    "Investigate recent quantity shift and commercial context":"Investigar el cambio reciente en cantidades y su contexto comercial",
    "Confirm purchasing cadence and whether zeros reflect availability":"Revisar la frecuencia de compra y si los ceros reflejan falta de disponibilidad",
    "Check volatile purchasing history before manual forecast override":"Revisar la volatilidad histórica antes de modificar manualmente el pronóstico",
    "Monitor SES forecast against incoming observations":"Comparar SES con las próximas observaciones"
}

def reason_label(value):
    if lang=="English":
        return value
    return "; ".join(reason_es.get(part.strip(),part.strip()) for part in str(value).split(";"))

tabs=st.tabs([
    T("Resultados principales","Key results"),
    T("Evaluación de modelos","Model performance"),
    T("Explorar productos","Product explorer"),
    T("Cartera ABC/XYZ","ABC/XYZ portfolio"),
    T("Centro de decisiones","Decision Center"),
    T("Errores retrospectivos","Retrospective exceptions")
])

with tabs[0]:
    st.subheader(T("¿Qué modelo conviene utilizar?","Which model should we use?"))
    a,b,c,d=st.columns(4)
    st.caption(T(
        "Comparamos el error porcentual absoluto ponderado (WAPE). Se calcula sobre las unidades observadas y, cuanto menor sea, mejor es el resultado.",
        "We compare weighted absolute percentage error (WAPE), calculated from observed units. Lower values mean less aggregate error."
    ))
    a.metric(T("Referencia (WAPE)","Baseline (WAPE)"),f"{naive:.2%}")
    b.metric(T("Suavizamiento simple (WAPE)","Exponential smoothing (WAPE)"),f"{ses:.2%}")
    c.metric(T("Por segmentos (WAPE)","Segment-based (WAPE)"),f"{seg:.2%}")
    d.metric(T("Menor error frente a referencia","Error reduction vs. baseline"),f"{reduction:.1%}")
    compare=policy[["strategy","wape"]].copy()
    compare["method"]=compare.strategy.map(labels)
    fig=px.bar(compare,x="method",y="wape",text=compare.wape.map(lambda x:f"{x:.2%}"),
               labels={"method":T("Método de pronóstico","Forecast method"),"wape":T("WAPE (menor es mejor)","WAPE (lower is better)")},
               title=T("Error de pronóstico en la evaluación final","Forecast error in the final evaluation"))
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
    st.write(T(
        "El suavizamiento exponencial simple, aplicado a cada producto con el mismo parámetro, tuvo el menor error agregado. Seleccionar modelos según ABC/XYZ no mejoró ese resultado, aunque la segmentación sigue siendo útil para organizar revisiones.",
        "Simple exponential smoothing, applied to each product using the same parameter, had the lowest aggregate error. Choosing models by ABC/XYZ segment did not improve that result, although segmentation still helps organize reviews."
    ))
    st.caption(T(
        "La evaluación final usa las semanas W44 a W51. Los métodos se seleccionaron con semanas anteriores. WAPE mide errores de cantidad, no pérdidas económicas ni problemas de inventario.",
        "The final evaluation covers weeks W44 to W51. Methods were selected using earlier weeks. WAPE measures quantity errors, not monetary losses or inventory shortfalls."
    ))

with tabs[1]:
    st.subheader(T("Qué cambia con el horizonte","How errors change by horizon"))
    h=horizons.copy()
    h["method"]=h.strategy.map(labels)
    graph=px.line(h,x="horizon",y="wape",color="method",markers=True,
        labels={"horizon":T("Semanas hacia adelante","Weeks ahead"),"wape":T("Error porcentual ponderado (WAPE)","Weighted percentage error (WAPE)"),"method":T("Método","Method")})
    graph.update_yaxes(tickformat=".0%")
    graph.update_xaxes(dtick=1)
    st.plotly_chart(graph,use_container_width=True)
    view=policy[["strategy","actual_units","absolute_error","wape","bias_pct"]].copy()
    view["strategy"]=view.strategy.map(labels)
    st.dataframe(view.rename(columns={
        "strategy":T("Modelo","Model"),
        "actual_units":T("Unidades observadas","Observed units"),
        "absolute_error":T("Error absoluto","Absolute error"),
        "wape":"WAPE",
        "bias_pct":T("Sesgo relativo","Relative bias")
    }),hide_index=True,use_container_width=True)
    st.caption(T(
        "La validación utilizó orígenes W32, W36 y W40. La prueba final utilizó W44 y W48. Cada predicción solo emplea semanas anteriores al origen.",
        "Selection used origins W32, W36 and W40. The final holdout used W44 and W48. Each forecast uses only weeks available before its origin."
    ))

with tabs[2]:
    st.subheader(T("Pronóstico y observaciones por producto","Forecasts and observations by product"))
    prod=st.selectbox(T("Producto","Product"),sorted(pred["product"].unique().tolist()))
    detail=pred[pred["product"]==prod].copy()
    detail["week_number"]=detail["origin"]+detail["horizon"]-1
    lines=detail.pivot_table(index="week_number",columns="model",values="forecast",aggfunc="first")
    lines["observed"]=detail.groupby("week_number").actual.first()
    lines=lines.sort_index()
    series=lines.rename(columns={
        "naive":T("Referencia: último valor","Baseline: last value"),
        "ses":T("Suavizamiento simple (SES)","Simple smoothing (SES)"),
        "observed":T("Observado","Observed")
    })
    st.line_chart(series)
    detail_view=detail[["origin","horizon","model","actual","forecast","abs_error"]].copy()
    detail_view["model"]=detail_view["model"].map(labels).fillna(detail_view["model"])
    st.dataframe(detail_view.rename(columns={
            "origin":T("Origen","Origin"),"horizon":T("Horizonte","Horizon"),
            "model":T("Modelo","Model"),"actual":T("Observado","Observed"),
            "forecast":T("Pronóstico","Forecast"),"abs_error":T("Error absoluto","Absolute error")
        }),hide_index=True,use_container_width=True)
    st.caption(T(
        "El resultado corresponde a cantidades observadas en una serie identificada de forma anónima. La precisión por producto puede variar considerablemente.",
        "These are observed quantities for an anonymous product series. Performance can vary considerably by product."
    ))

with tabs[3]:
    st.subheader(T("Segmentación de la cartera","Portfolio segmentation"))
    a,b,c=st.columns(3)
    a.metric(T("Productos","Products"),f"{len(profile):,}")
    b.metric(T("Unidades históricas","Historical units"),f"{profile.historical_units.sum():,.0f}")
    c.metric(T("Clase A","Class A"),f"{(profile.abc=='A').sum():,}")
    st.write(T(
        "ABC agrupa productos por concentración de unidades históricas. XYZ describe la variación semanal de las cantidades compradas.",
        "ABC groups products by historical unit-volume concentration. XYZ describes the variation in weekly purchased quantities."
    ))
    st.dataframe(pd.crosstab(profile.abc,profile.xyz).rename_axis("ABC"),use_container_width=True)
    cat=st.multiselect("ABC",["A","B","C"],default=["A","B","C"])
    xyz=st.multiselect("XYZ",["X","Y","Z"],default=["X","Y","Z"])
    shown=profile[profile.abc.isin(cat)&profile.xyz.isin(xyz)].copy()
    st.dataframe(shown[["product","abc","xyz","historical_units","zero_share","demand_pattern"]]
        .rename(columns={"product":T("Producto","Product"),
                         "historical_units":T("Unidades históricas","Historical units"),
                         "zero_share":T("Proporción de semanas en cero","Share of zero weeks"),
                         "demand_pattern":T("Patrón descriptivo","Descriptive pattern")}),
        hide_index=True,use_container_width=True)
    st.caption(T(
        "Estas clases no representan ingresos, margen o importancia estratégica. Los patrones son descriptivos y no prueban demanda sin restricciones.",
        "These classes do not represent revenue, margin or strategic importance. Patterns are descriptive and do not prove unconstrained demand."
    ))

with tabs[4]:
    st.subheader(T("Qué productos merecen una revisión","Which products deserve a closer look"))
    a,b,c=st.columns(3)
    for col,k in zip([a,b,c],["High","Medium","Routine"]):
        col.metric(tiers[k],int((queue.review_tier==k).sum()))
    st.caption(T(
        "Prioridades calculadas solo con W0 a W43. No se utilizaron las observaciones posteriores de la prueba final para ordenar esta cola.",
        "Priorities are based only on W0 to W43. Later holdout outcomes were not used to rank this queue."
    ))
    selected=st.multiselect(T("Nivel de revisión","Review tier"),list(tiers),
                           default=list(tiers),format_func=lambda x:tiers[x])
    q=queue[queue.review_tier.isin(selected)].copy()
    q["review_tier"]=q.review_tier.map(tiers)
    if lang=="Español":
        q["review_reason"]=q.review_reason.map(reason_label)
        q["recommended_review"]=q.recommended_review.map(lambda x:actions_es.get(x,x))
    cols=["product","abc","xyz","review_tier","review_score","historical_units",
          "forecast_next_week","forecast_four_week_total","recent_shift_units",
          "review_reason","recommended_review"]
    st.dataframe(q[cols].rename(columns={
        "product":T("Producto","Product"),"review_tier":T("Nivel","Tier"),
        "review_score":T("Puntuación","Score"),"historical_units":T("Unidades históricas","Historical units"),
        "forecast_next_week":T("Próxima semana","Next week"),
        "forecast_four_week_total":T("Próximas 4 semanas","Next 4 weeks"),
        "recent_shift_units":T("Cambio reciente (unidades)","Recent shift (units)"),
        "review_reason":T("Motivos","Reasons"),"recommended_review":T("Revisión sugerida","Suggested review")
    }),hide_index=True,use_container_width=True)
    st.info(T(
        "La puntuación es una regla transparente para organizar trabajo humano. No es una probabilidad de desabasto, un riesgo monetario ni una orden de reabastecimiento.",
        "The score is a transparent human-review heuristic. It is not a stockout probability, monetary exposure or replenishment order."
    ))

with tabs[5]:
    st.subheader(T("Errores observados en la evaluación final","Observed errors on the final holdout"))
    high=st.checkbox(T("Solo productos de mayor volumen","High historical volume only"))
    e=exceptions[exceptions.high_volume] if high else exceptions
    fields=["product","historical_units","zero_share","selected_abs_error",
            "baseline_abs_error","improvement_units","exception_reason"]
    reasons={
        "High volume and high absolute error":T("Alto volumen y error elevado","High volume and high absolute error"),
        "Selected model worse than naive":T("SES con mayor error que el modelo de referencia","SES error higher than the baseline"),
        "Same-sign bias at both origins":T("Sesgo del mismo signo en ambos orígenes","Same-sign bias at both origins"),
        "High share of zero weeks":T("Muchas semanas sin compras","High share of zero weeks"),
        "Routine monitoring":T("Seguimiento ordinario","Routine monitoring")
    }
    e=e.copy()
    e["exception_reason"]=e.exception_reason.map(lambda x:reasons.get(x,x))
    st.dataframe(e[fields].head(250).rename(columns={
        "product":T("Producto","Product"),
        "historical_units":T("Unidades históricas","Historical units"),
        "zero_share":T("Semanas en cero","Zero-week share"),
        "selected_abs_error":T("Error absoluto SES (unidades)","SES absolute error (units)"),
        "baseline_abs_error":T("Error absoluto de referencia (unidades)","Baseline absolute error (units)"),
        "improvement_units":T("Mejora en unidades","Improvement in units"),
        "exception_reason":T("Diagnóstico","Diagnostic")
    }),hide_index=True,use_container_width=True)
    st.caption(T(
        "Esta lista usa errores observados en el holdout. Sirve para diagnóstico posterior, no para afirmar que habríamos conocido esos errores con anticipación.",
        "This list uses observed holdout errors. It is retrospective diagnostics, not a claim that those errors were known ahead of time."
    ))

st.divider()
st.caption(T(
    "Fuente: Tan (2014), UCI Sales Transactions Weekly, CC BY 4.0. Semanas relativas, sin fechas de calendario ni inventario. Caso de portafolio de Carlos Segura.",
    "Source: Tan (2014), UCI Sales Transactions Weekly, CC BY 4.0. Relative weeks, no calendar dates or inventory. Portfolio case by Carlos Segura."
))
