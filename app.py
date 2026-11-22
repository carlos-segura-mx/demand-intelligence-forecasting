"""Bilingual Streamlit dashboard for the UCI weekly forecasting case."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"
NEEDED=[
    "model_summary.csv","final_predictions.csv","decision_exceptions.csv",
    "portfolio_profile.csv","policy_overall_metrics.csv","policy_segment_metrics.csv",
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
segments=load("policy_segment_metrics.csv")
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
    "naive":T("Base","Baseline"),
    "ses":"SES",
    "segmented_policy":"ABC/XYZ"
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
    a.metric(T("WAPE base","Baseline WAPE"),f"{naive:.2%}")
    b.metric("WAPE SES",f"{ses:.2%}")
    c.metric("WAPE ABC/XYZ",f"{seg:.2%}")
    d.metric(T("Mejora vs. base","Gain vs. baseline"),f"{reduction:.1%}")
    st.caption(T(
        "La mejora es una reducción relativa del error absoluto total, no una diferencia en puntos porcentuales de WAPE.",
        "The gain is the relative reduction in total absolute error, not a percentage-point difference in WAPE."
    ))
    compare=policy[["strategy","wape"]].copy()
    compare["method"]=compare.strategy.map(labels)
    compare["method"]=pd.Categorical(
        compare["method"],categories=[labels["naive"],labels["ses"],labels["segmented_policy"]],
        ordered=True)
    compare=compare.sort_values("method")
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
        "Evaluación final: W44 a W51. Se eligieron los métodos con semanas anteriores. WAPE mide error en cantidades, no pérdidas económicas.",
        "Final evaluation: W44 to W51. Methods were selected on earlier weeks. WAPE measures quantity error, not financial losses."
    ))
    with st.expander(T("¿Qué significan los métodos?", "What do the methods mean?")):
        st.write(T(
            "Base repite la última cantidad semanal observada para cada semana del horizonte. SES significa suavizamiento exponencial simple: actualiza un nivel por producto con alfa de 0.3. ABC/XYZ elige un método por segmento mediante validación histórica. WAPE es la suma de errores absolutos dividida entre la suma de unidades observadas; menor es mejor.",
            "Baseline repeats the last observed weekly quantity across the forecast horizon. SES means simple exponential smoothing: it updates each product's level with alpha 0.3. ABC/XYZ chooses a model by segment using prior validation. WAPE is total absolute error divided by total observed units; lower is better."
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
    view["wape"]=(100*view["wape"]).round(2)
    view["bias_pct"]=(100*view["bias_pct"]).round(2)
    view["absolute_error"]=view["absolute_error"].round(1)
    st.dataframe(view.rename(columns={
        "strategy":T("Modelo","Model"),
        "actual_units":T("Unidades observadas","Observed units"),
        "absolute_error":T("Error absoluto","Absolute error"),
        "wape":"WAPE (%)",
        "bias_pct":T("Sesgo (%)","Bias (%)")
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
        "naive":T("Base","Baseline"),
        "ses":"SES",
        "observed":T("Observado","Observed")
    })
    st.caption(T(
        "Evaluación histórica: semanas indexadas W44 a W51. No son fechas de calendario ni un pronóstico vigente.",
        "Historical evaluation: indexed weeks W44 to W51. These are not calendar dates or current forecasts."
    ))
    st.line_chart(series)
    detail_view=detail[["origin","horizon","model","actual","forecast","abs_error"]].copy()
    detail_view["model"]=detail_view["model"].map(labels).fillna(detail_view["model"])
    detail_view[["forecast","abs_error"]]=detail_view[["forecast","abs_error"]].round(2)
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

    st.subheader(T("Error por segmento ABC/XYZ","Error by ABC/XYZ segment"))
    st.write(T(
        "El WAPE agregado puede ocultar dificultades en productos con pocas unidades o compras irregulares. Esta matriz permite comparar segmentos, no estimar su rentabilidad.",
        "Aggregate WAPE can hide forecasting challenges in low-volume or irregularly purchased products. This matrix compares segments, not their profitability."
    ))
    strategy=st.selectbox(
        T("Método de la matriz","Matrix method"),
        ["ses","naive","segmented_policy"],
        format_func=lambda x:labels[x],key="segment_method")
    segment_view=segments.loc[segments.strategy.eq(strategy)].copy()
    segment_matrix=(segment_view.pivot(index="abc",columns="xyz",values="wape")
                    .reindex(index=["A","B","C"],columns=["X","Y","Z"]))
    cells=[[f"{v:.1%}" if pd.notna(v) else "" for v in row] for row in segment_matrix.to_numpy()]
    heat=go.Figure(data=go.Heatmap(
        z=100*segment_matrix.to_numpy(),x=["X","Y","Z"],y=["A","B","C"],
        text=cells,texttemplate="%{text}",
        hovertemplate="ABC %{y} / XYZ %{x}<br>WAPE %{z:.1f}%<extra></extra>",
        colorscale="Blues",colorbar={"title":"WAPE (%)"}))
    heat.update_layout(height=330,margin={"l":30,"r":15,"t":20,"b":35},
                       xaxis_title="XYZ",yaxis_title="ABC",yaxis_autorange="reversed")
    for abc_name in segment_matrix.index:
        for xyz_name in segment_matrix.columns:
            if pd.isna(segment_matrix.loc[abc_name,xyz_name]):
                heat.add_annotation(x=xyz_name,y=abc_name,
                                    text=T("N/D","N/A"),showarrow=False,
                                    font={"color":"#bdbdbd","size":12})
    heat.update_traces(hoverongaps=False)
    st.plotly_chart(heat,use_container_width=True)
    st.caption(T(
        "N/D indica segmentos sin pronósticos evaluados, no un error de 0 %. Los porcentajes requieren interpretación junto con el volumen observado.",
        "N/A means there were no evaluated forecasts in that segment, not a 0% error. Read percentages alongside observed volume."
    ))
    segment_view["segment"]=segment_view.abc+segment_view.xyz
    segment_view["wape_display"]=(100*segment_view.wape).round(2)
    segment_view["bias_display"]=(100*segment_view.bias_pct).round(2)
    st.dataframe(segment_view[["segment","actual_units","n","wape_display","bias_display"]]
        .rename(columns={
            "segment":T("Segmento","Segment"),
            "actual_units":T("Unidades observadas","Observed units"),
            "n":T("Pronósticos evaluados","Evaluated forecasts"),
            "wape_display":"WAPE (%)",
            "bias_display":T("Sesgo (%)","Bias (%)")}),
        hide_index=True,use_container_width=True)
    st.caption(T(
        "ABC se basa en unidades, no en ingresos o márgenes. Los segmentos con pocas unidades requieren cautela al interpretar porcentajes altos.",
        "ABC uses unit volume, not revenue or margins. Interpret high percentage errors cautiously for segments with few observed units."
    ))

    cat=st.multiselect("ABC",["A","B","C"],default=["A","B","C"])
    xyz=st.multiselect("XYZ",["X","Y","Z"],default=["X","Y","Z"])
    shown=profile[profile.abc.isin(cat)&profile.xyz.isin(xyz)].copy()
    shown["zero_share"]=(100*shown.zero_share).round(1)
    pattern_es={"smooth":"Estable","erratic":"Errático","intermittent":"Intermitente",
                "lumpy":"Irregular","all_zero":"Sin compras","unknown":"Sin clasificar"}
    if lang=="Español":
        shown["demand_pattern"]=shown["demand_pattern"].map(lambda x:pattern_es.get(x,x))
    st.dataframe(shown[["product","abc","xyz","historical_units","zero_share","demand_pattern"]]
        .rename(columns={"product":T("Producto","Product"),
                         "historical_units":T("Unidades históricas","Historical units"),
                         "zero_share":T("Semanas sin compras (%)","Zero weeks (%)"),
                         "demand_pattern":T("Patrón descriptivo","Descriptive pattern")}),
        hide_index=True,use_container_width=True)
    st.caption(T(
        "Estas clases no representan ingresos, margen o importancia estratégica. Los patrones son descriptivos y no prueban demanda sin restricciones.",
        "These classes do not represent revenue, margin or strategic importance. Patterns are descriptive and do not prove unconstrained demand."
    ))

with tabs[4]:
    st.subheader(T("Qué productos conviene revisar","Which products should be reviewed"))
    a,b,c=st.columns(3)
    for col,k in zip([a,b,c],["High","Medium","Routine"]):
        col.metric(tiers[k],int((queue.review_tier==k).sum()))
    st.caption(T(
        "Corte histórico: W43. Los pronósticos corresponden a W44 y W44 a W47, no al calendario actual.",
        "Historical cutoff: W43. Forecasts refer to W44 and W44 to W47, not the current calendar."
    ))
    st.info(T(
        "La prioridad de revisión combina volumen histórico (ABC), variabilidad (XYZ), semanas sin compras y cambios recientes. No mide impacto económico ni identifica automáticamente los productos más rentables. Por eso se presentan dos enfoques de revisión.",
        "Review priority combines historical volume (ABC), variability (XYZ), zero-purchase weeks and recent changes. It does not measure financial impact or identify the most profitable products. Two complementary review perspectives are provided."
    ))
    focus=st.radio(
        T("Enfoque de revisión","Review focus"),
        ["patterns","volume"],horizontal=True,
        format_func=lambda x:(
            T("Alertas por patrones","Pattern alerts") if x=="patterns"
            else T("Mayor volumen histórico","Highest historical volume")
        ),key="review_focus")
    selected=st.multiselect(
        T("Prioridad de revisión","Review priority"),list(tiers),
        default=list(tiers),format_func=lambda x:tiers[x])
    q=queue[queue.review_tier.isin(selected)].copy()
    if focus=="volume":
        q=q.sort_values(
            ["historical_units","review_score","product"],
            ascending=[False,False,True],kind="stable")
        st.caption(T(
            "Ordenado por unidades históricas. Más unidades no implica mayor margen ni riesgo monetario.",
            "Sorted by historical units. More units do not imply higher margins or monetary risk."
        ))
    else:
        q=q.sort_values(
            ["review_score","historical_units","product"],
            ascending=[False,False,True],kind="stable")
        st.caption(T(
            "Ordenado por puntuación de revisión. Los patrones irregulares pueden destacar incluso cuando el volumen es bajo.",
            "Sorted by review score. Irregular patterns can rank highly even with low unit volume."
        ))
    q["review_tier"]=q.review_tier.map(tiers)
    if lang=="Español":
        q["review_reason"]=q.review_reason.map(reason_label)
        q["recommended_review"]=q.recommended_review.map(lambda x:actions_es.get(x,x))
    export_cols=["product","abc","xyz","review_tier","review_score","historical_units",
                 "forecast_next_week","forecast_four_week_total","recent_shift_units",
                 "review_reason","recommended_review"]
    export_names={
        "product":T("Producto","Product"),
        "review_tier":T("Prioridad de revisión","Review priority"),
        "review_score":T("Puntuación","Score"),
        "historical_units":T("Unidades históricas","Historical units"),
        "forecast_next_week":T("Pronóstico W44","W44 forecast"),
        "forecast_four_week_total":T("Pronóstico W44 a W47","W44 to W47 forecast"),
        "recent_shift_units":T("Cambio reciente (unidades)","Recent shift (units)"),
        "review_reason":T("Motivos","Reasons"),
        "recommended_review":T("Revisión sugerida","Suggested review")
    }
    export_view=q[export_cols].rename(columns=export_names)
    display_view=q[["product","abc","xyz","review_tier","review_score",
                    "historical_units","forecast_next_week","recent_shift_units"]].copy()
    display_view["abc_xyz"]=display_view.abc+display_view.xyz
    display_view["forecast_next_week"]=display_view.forecast_next_week.round(2)
    display_view=display_view[["product","abc_xyz","review_tier","review_score",
                               "historical_units","forecast_next_week","recent_shift_units"]]
    display_view=display_view.rename(columns={
        "product":T("Producto","Product"),
        "abc_xyz":T("Segmento","Segment"),
        "review_tier":T("Prioridad","Priority"),
        "review_score":T("Puntos","Score"),
        "historical_units":T("Unidades","Historical units"),
        "forecast_next_week":T("Pronóstico W44","W44 forecast"),
        "recent_shift_units":T("Cambio reciente","Recent change")
    })
    visible=st.selectbox(
        T("Mostrar productos","Show products"),[10,20,50,"all"],
        index=1,format_func=lambda x:T("Todos","All") if x=="all" else str(x),
        key="review_row_count")
    st.dataframe(display_view if visible=="all" else display_view.head(visible),
                 hide_index=True,use_container_width=True)
    st.download_button(
        T("Descargar lista filtrada (CSV)","Download filtered review list (CSV)"),
        data=export_view.to_csv(index=False).encode("utf-8-sig"),
        file_name="demand_review_queue.csv",mime="text/csv")
    if not q.empty:
        st.subheader(T("Detalle para revisar","Product review details"))
        chosen_product=st.selectbox(
            T("Producto seleccionado","Selected product"),
            q["product"].tolist(),key="review_product_detail")
        selected_row=q.loc[q["product"].eq(chosen_product)].iloc[0]
        st.write(T("**Motivos:** ","**Reasons:** ")+str(selected_row.review_reason))
        st.write(T("**Revisión sugerida:** ","**Suggested review:** ")
                 +str(selected_row.recommended_review))
        st.caption(T(
            "La lista resumida muestra pronósticos con dos decimales; el archivo CSV conserva la precisión calculada.",
            "The summary table rounds forecasts to two decimals; the CSV retains calculated precision."
        ))
        top=q.head(15).iloc[::-1].copy()
        chart=px.bar(top,x="historical_units",y="product",orientation="h",
                     color="review_tier",
                     labels={
                         "historical_units":T("Unidades históricas","Historical units"),
                         "product":T("Producto","Product"),
                         "review_tier":T("Prioridad","Priority")
                     },
                     title=T(
                         "Volumen de los primeros 15 productos según el enfoque elegido",
                         "Historical volume of the first 15 products under the selected view"
                     ))
        st.plotly_chart(chart,use_container_width=True)
    else:
        st.warning(T(
            "No hay productos para los filtros seleccionados.",
            "No products match the selected filters."
        ))
    st.caption(T(
        "Las prioridades son reglas de revisión definidas por el analista, no probabilidades calibradas de desabasto, pérdidas económicas ni órdenes de compra.",
        "Priorities are analyst-defined review rules, not calibrated stockout probabilities, financial losses or purchase orders."
    ))

with tabs[5]:
    st.subheader(T("Errores observados en la evaluación final","Observed errors on the final holdout"))
    high=st.checkbox(T("Solo productos de mayor volumen","High historical volume only"))
    e=exceptions[exceptions.high_volume] if high else exceptions
    fields=["product","historical_units","zero_share","selected_abs_error",
            "baseline_abs_error","improvement_units","exception_reason"]
    reasons={
        "High volume and high absolute error":T("Alto volumen y error elevado","High volume and high absolute error"),
        "Selected model worse than naive":T("SES supera el error base","SES error exceeds baseline"),
        "Same-sign bias at both origins":T("Sesgo del mismo signo en ambos orígenes","Same-sign bias at both origins"),
        "High share of zero weeks":T("Muchas semanas sin compras","High share of zero weeks"),
        "Routine monitoring":T("Seguimiento ordinario","Routine monitoring")
    }
    e=e.copy()
    e["exception_reason"]=e.exception_reason.map(lambda x:reasons.get(x,x))
    e["zero_share"]=(100*e["zero_share"]).round(1)
    st.dataframe(e[fields].head(250).rename(columns={
        "product":T("Producto","Product"),
        "historical_units":T("Unidades históricas","Historical units"),
        "zero_share":T("Semanas sin compras (%)","Zero weeks (%)"),
        "selected_abs_error":T("Error absoluto SES (unidades)","SES absolute error (units)"),
        "baseline_abs_error":T("Error absoluto de referencia (unidades)","Baseline absolute error (units)"),
        "improvement_units":T("Reducción del error (unidades)","Error reduction (units)"),
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
