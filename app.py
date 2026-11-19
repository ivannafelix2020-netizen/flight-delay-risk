"""Flight Delay Risk | Dashboard interactivo de riesgo de retrasos."""
import json
from datetime import date, timedelta
from pathlib import Path
import html

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Flight Delay Risk | Analytics", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {--navy:#10263F;--teal:#007F86;--coral:#ED795B;--muted:#63758A;--bg:#F5F8FC;}
html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans',sans-serif;}
[data-testid="stAppViewContainer"] {background:#F5F8FC;}
[data-testid="stSidebar"] {background:#10263F;}
[data-testid="stSidebar"] * {color:#F3F7FA !important;}
[data-testid="stSidebar"] input {color:#10263F !important;}
[data-testid="stSidebar"] [data-testid="stDateInput"] input {color:#10263F !important;}
h1,h2,h3 {font-family:'Manrope',sans-serif !important;letter-spacing:-.035em;color:#10263F;}
h2 {font-size:1.45rem !important;}
.block-container {max-width:1330px;padding-top:1.8rem;padding-bottom:3rem;}
.hero {background:linear-gradient(115deg,#10263F 0%,#16415A 66%,#007F86 130%);border-radius:22px;padding:33px 38px;margin-bottom:25px;color:white;box-shadow:0 12px 28px #10263F16;}
.hero .eyebrow {color:#9AE1DE;font-weight:800;font-size:.73rem;letter-spacing:.18em;}
.hero h1 {font-size:clamp(2rem,4vw,3.25rem);line-height:1.12;margin:10px 0 12px;color:#fff !important;}
.hero p {color:#E1EDF2;font-size:1.05rem;max-width:770px;margin:0;}
.hero .pills {display:flex;gap:9px;flex-wrap:wrap;margin-top:20px;}
.hero .pill {background:#FFFFFF18;border:1px solid #FFFFFF30;border-radius:100px;padding:7px 12px;font-size:.8rem;color:#EAF8FA;}
.metric-card {background:white;border:1px solid #E3EAF1;border-radius:17px;padding:20px 23px;min-height:126px;box-shadow:0 4px 18px #12294208;}
.metric-card .label {font-size:.8rem;color:#64758A;font-weight:700;letter-spacing:.02em;}
.metric-card .value {font-family:'Manrope',sans-serif;font-size:1.85rem;font-weight:800;color:#10263F;margin-top:8px;}
.metric-card .detail {font-size:.78rem;color:#718298;margin-top:2px;}
.section-kicker {font-size:.73rem;font-weight:800;letter-spacing:.15em;color:#007F86;margin-bottom:4px;}
.note {background:#ECF8F7;border:1px solid #BCE8E2;border-left:4px solid #007F86;border-radius:13px;padding:17px 19px;color:#183D48;}
.note strong {color:#006D73;}
div[data-testid="stForm"] {background:white;border:1px solid #E1E9F0;border-radius:19px;padding:22px 24px;box-shadow:0 5px 24px #10263F08;}
div.stButton>button[kind="primary"], div[data-testid="stFormSubmitButton"] button {background:#007F86;border:0;border-radius:11px;font-weight:700;padding:11px 21px;}
div.stButton>button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover {background:#00656B;border:0;}
[data-testid="stDataFrame"] {border-radius:14px;overflow:hidden;}
.small-muted {color:#708198;font-size:.83rem;}

/* Contraste consistente en el contenido principal: evita texto blanco heredado del tema oscuro */
[data-testid="stMain"] {color:#17324B !important;}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3,[data-testid="stMain"] h4,
[data-testid="stMain"] p,[data-testid="stMain"] label,[data-testid="stMain"] label p,
[data-testid="stMain"] [data-testid="stWidgetLabel"],
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stExpanderDetails"] p {color:#17324B !important;}
[data-testid="stMain"] [data-testid="stWidgetLabel"] {font-weight:700 !important;}
[data-testid="stMain"] [data-testid="stForm"] label p {color:#17324B !important;opacity:1 !important;}
[data-testid="stMain"] [data-testid="stForm"] [data-baseweb="select"],
[data-testid="stMain"] [data-testid="stForm"] input {color:#F8FAFC !important;}
[data-testid="stMain"] [data-testid="stForm"] [data-baseweb="select"] * {color:#F8FAFC !important;}
[data-testid="stMain"] [data-testid="stForm"] input:disabled {color:#CBD5E1 !important;-webkit-text-fill-color:#CBD5E1 !important;}
[data-testid="stMain"] [data-testid="stExpander"] {background:#FFFFFF;border:1px solid #DCE7EE;border-radius:13px;overflow:hidden;margin-bottom:12px;}
[data-testid="stMain"] [data-testid="stExpander"] summary {background:#EAF2F6 !important;color:#17324B !important;}
[data-testid="stMain"] [data-testid="stExpander"] summary p,
[data-testid="stMain"] [data-testid="stExpander"] summary span {color:#17324B !important;font-weight:700 !important;}
[data-testid="stMain"] [data-testid="stExpanderDetails"] {background:#FFFFFF !important;padding:12px 17px;}
[data-testid="stMain"] [data-testid="stAlert"] p {color:#17324B !important;}
[data-testid="stMain"] .hero h1,[data-testid="stMain"] .hero p {color:#FFFFFF !important;}
[data-testid="stMain"] .hero .eyebrow {color:#9AE1DE !important;}
[data-testid="stMain"] .hero .pill {color:#EAF8FA !important;}
[data-testid="stMain"] .section-kicker {color:#007F86 !important;}
[data-testid="stMain"] .metric-card .label,[data-testid="stMain"] .metric-card .detail {color:#64758A !important;}
[data-testid="stMain"] .metric-card .value {color:#10263F !important;}
[data-testid="stMain"] .note,[data-testid="stMain"] .note strong {color:#17324B !important;}
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button p {color:#FFFFFF !important;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_assets():
    config = json.loads((ROOT / "configuracion.json").read_text(encoding="utf-8"))
    model = joblib.load(ROOT / config["modelo_activo"])
    history = pd.read_csv(ROOT / "historial.csv", parse_dates=["FlightDate"])
    history["ArrDel15"] = history["ArrDel15"].astype(int)
    return config, model, history

config, model, history = load_assets()
FRANJAS = {int(k): v for k, v in config["mapa_franjas"].items()}
FEATURES = config["features"]
AIRLINES = sorted(history["Reporting_Airline"].unique().tolist())
HORIZONS = config["anticipaciones_validadas"]
LAG = config["retraso_publicacion_supuesto"]
ALPHA = config["alpha_suavizado"]
PRIOR = config["prior_inicial"]


def historical_counts(hist, cutoff, filters=None, days=None):
    # BTS publication lag is a modeling assumption; strict cutoff excludes same-day outcomes.
    subset = hist[hist["FlightDate"] < cutoff]
    if days is not None:
        subset = subset[subset["FlightDate"] >= cutoff - pd.Timedelta(days=days)]
    for col, value in (filters or {}).items():
        subset = subset[subset[col] == value]
    return len(subset), int(subset["ArrDel15"].sum())


def predict_flight(origin, airline, flight_date, departure, duration, consultation_date):
    flight_date = pd.Timestamp(flight_date).normalize()
    consultation_date = pd.Timestamp(consultation_date).normalize()
    days = int((flight_date - consultation_date).days)
    if days not in HORIZONS:
        raise ValueError("Selecciona una fecha de vuelo exactamente a 30, 60, 90 o 180 días de la consulta.")
    if origin not in ("JFK", "SFO") or airline not in AIRLINES:
        raise ValueError("Ruta o aerolínea no reconocida.")
    if duration <= 0:
        raise ValueError("La duración programada debe ser positiva.")
    if departure.hour not in FRANJAS:
        raise ValueError("La hora seleccionada no tiene una franja horaria observada en entrenamiento.")
    if flight_date <= consultation_date:
        raise ValueError("El vuelo debe ser posterior a la consulta.")

    cutoff = consultation_date - pd.Timedelta(days=LAG)
    n_global, y_global = historical_counts(history, cutoff)
    prior = (y_global + ALPHA * PRIOR) / (n_global + ALPHA)
    band = FRANJAS[departure.hour]
    specs = [
        ("riesgo_historico_ruta", {"Origin": origin}, None),
        ("riesgo_historico_aerolinea_ruta", {"Origin": origin, "Reporting_Airline": airline}, None),
        ("riesgo_historico_horario_ruta", {"Origin": origin, "franja_horaria": band}, None),
        ("riesgo_reciente_ruta_90d", {"Origin": origin}, 90),
    ]
    row = {
        "Origin": origin, "Reporting_Airline": airline,
        "Month": flight_date.month, "DayOfWeek": flight_date.dayofweek + 1,
        "franja_horaria": band,
        "minuto_salida": departure.hour * 60 + departure.minute,
        "duracion_horas": float(duration) / 60,
        "dias_anticipacion": days,
        "prior_historico": prior,
    }
    for key, filters, window in specs:
        n, y = historical_counts(history, cutoff, filters, window)
        row[key] = (y + ALPHA * prior) / (n + ALPHA)
    probability = float(model.predict_proba(pd.DataFrame([row])[FEATURES])[0, 1])
    return {
        "Ruta": f"{origin} → LAX", "Aerolínea": airline,
        "Fecha": flight_date.date().isoformat(),
        "Salida": departure.strftime("%H:%M"),
        "Duración (min)": int(duration),
        "Anticipación": days,
        "Probabilidad": probability,
        "Corte histórico": cutoff.date().isoformat(),
        "Registros históricos": n_global,
    }


st.markdown("""
<div class="hero">
  <div class="eyebrow">AVIATION ANALYTICS / DECISION INTELLIGENCE</div>
  <h1>Flight Delay Risk <span style="color:#8FE0DA">✈</span></h1>
  <p>Compara vuelos con datos históricos y estima el riesgo de llegar <b>15 minutos o más tarde</b> antes de comprar tu boleto.</p>
  <div class="pills"><span class="pill">JFK → LAX</span><span class="pill">SFO → LAX</span><span class="pill">Regresión logística</span><span class="pill">Predicción basada en datos</span></div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ✈️ Flight Delay Risk")
    st.caption("PANEL DE CONFIGURACIÓN")
    consultation = st.date_input("Fecha de consulta", value=date.today())
    st.caption(f"Se supone un desfase de publicación histórica de {LAG} días; no es una verificación de disponibilidad BTS en tiempo real.")
    st.divider()
    st.markdown("**Información del modelo**")
    st.write("Regresión logística original")
    st.write(f"Último vuelo registrado: {config['ultima_fecha_historica']}")
    st.caption("Los datos no se actualizan automáticamente.")

if "options" not in st.session_state:
    st.session_state.options = []

st.markdown('<div class="section-kicker">01 / DEFINE TU VUELO</div>', unsafe_allow_html=True)
st.subheader("Configura una opción")
st.caption("Selecciona el aeropuerto de origen y la aerolínea. El destino siempre es LAX (Los Ángeles). La hora corresponde al aeropuerto de salida.")
with st.form("flight_form", clear_on_submit=False):
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        origin = st.selectbox("Aeropuerto de origen", ["JFK", "SFO"])
        airline = st.selectbox("Aerolínea · código BTS", AIRLINES)
    with c2:
        st.text_input("Aeropuerto de destino", value="LAX — Los Ángeles", disabled=True)
        horizon = st.selectbox("Anticipación de compra (días)", HORIZONS, index=2)
        flight_date = consultation + timedelta(days=int(horizon))
        st.text_input("Fecha del vuelo (calculada)", value=flight_date.isoformat(), disabled=True)
    with c3:
        departure = st.time_input("Hora de salida programada (origen)", value=pd.Timestamp("10:00").time(), step=1800)
        duration = st.number_input("Duración prevista del vuelo (minutos)", min_value=1, max_value=1000, value=90 if origin == "SFO" else 360)
    add = st.form_submit_button("✈ Calcular riesgo y agregar vuelo", type="primary", use_container_width=True)

if add:
    try:
        result = predict_flight(origin, airline, flight_date, departure, duration, consultation)
        unique_keys = ("Ruta", "Aerolínea", "Fecha", "Salida", "Duración (min)", "Anticipación")
        duplicate = any(all(option[key] == result[key] for key in unique_keys) for option in st.session_state.options)
        if duplicate:
            st.info("Este vuelo ya está incluido en la comparación. Modifica algún dato para agregar otra opción.")
        else:
            st.session_state.options.append(result)
            st.success(f"Vuelo agregado · Riesgo estimado: {result['Probabilidad']:.1%}")
    except ValueError as exc:
        st.error(str(exc))

st.markdown('<div class="section-kicker" style="margin-top:30px">02 / ANALIZA LAS OPCIONES</div>', unsafe_allow_html=True)
st.subheader("Comparación de vuelos")

if st.session_state.options:
    df = pd.DataFrame(st.session_state.options).sort_values("Probabilidad", ascending=True).reset_index(drop=True)
    best = df.iloc[0]
    count = len(df)
    spread = (df["Probabilidad"].max() - df["Probabilidad"].min()) * 100
    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        st.markdown(f'<div class="metric-card"><div class="label">VUELOS COMPARADOS</div><div class="value">{count}</div><div class="detail">Opciones únicas analizadas</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="label">MENOR RIESGO ESTIMADO</div><div class="value" style="color:#007F86">{best["Probabilidad"]:.1%}</div><div class="detail">{html.escape(best["Ruta"])} · {html.escape(str(best["Aerolínea"]))}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="label">DIFERENCIA ENTRE EXTREMOS</div><div class="value">{spread:.1f} pp</div><div class="detail">Puntos porcentuales estimados</div></div>', unsafe_allow_html=True)

    st.markdown("#### Riesgo estimado por vuelo")
    st.caption("Barras ordenadas de menor a mayor riesgo estimado. Turquesa: opción con menor riesgo entre las ingresadas.")
    labels = [f'{r["Ruta"]}  |  {r["Aerolínea"]}  |  {r["Salida"]}  |  {r["Fecha"]}' for _, r in df.iterrows()]
    vals = df["Probabilidad"].to_numpy() * 100
    colors = ["#007F86" if i == 0 else "#6B91A7" for i in range(len(df))]
    fig, ax = plt.subplots(figsize=(11, max(2.6, 0.7 * count + 1.0)))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    y = np.arange(count)
    ax.barh(y, vals, color=colors, height=0.53, zorder=3)
    ax.set_yticks(y, labels=labels, fontsize=10, color="#233D52")
    ax.invert_yaxis()
    max_axis = max(30.0, float(vals.max()) * 1.22)
    ax.set_xlim(0, min(100, max_axis))
    ax.set_xlabel("Probabilidad estimada de retraso (%)", fontsize=10, color="#61748A", labelpad=10)
    ax.grid(axis="x", color="#E7EDF2", zorder=0)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(axis="both", length=0, pad=9)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    for i, v in enumerate(vals):
        ax.text(min(v + max_axis * .012, 98), i, f"{v:.1f}%", va="center", fontsize=11, fontweight="bold", color="#10263F")
    fig.tight_layout(pad=1.8)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("#### Detalle de cada opción")
    show = df.copy()
    show["Probabilidad"] = show["Probabilidad"].map(lambda v: f"{v:.1%}")
    show["Registros históricos"] = show["Registros históricos"].map(lambda v: f"{v:,}")
    st.dataframe(show, hide_index=True, use_container_width=True)
    st.markdown(f'<div class="note"><strong>✦ Opción con menor riesgo estimado:</strong> {html.escape(best["Ruta"])} · {html.escape(str(best["Aerolínea"]))} · {html.escape(best["Salida"])} — <strong>{best["Probabilidad"]:.1%}</strong>.<div class="small-muted" style="margin-top:6px">Comparación relativa entre las opciones ingresadas; no garantiza puntualidad.</div></div>', unsafe_allow_html=True)
    st.write("")
    if st.button("🗑️ Borrar comparación"):
        st.session_state.options = []
        st.rerun()
else:
    st.info("Agrega dos o más vuelos para comparar sus riesgos estimados. Puedes comenzar con uno.")

st.markdown('<div class="section-kicker" style="margin-top:32px">03 / CONTEXTO Y LIMITACIONES</div>', unsafe_allow_html=True)
st.subheader("Cómo interpretar los resultados")
st.markdown("Las siguientes notas explican **qué predice el modelo**, qué datos utiliza y cuáles son sus limitaciones. Despliega cada apartado para conocer los detalles.")
with st.expander("¿Qué significa la probabilidad de retraso?", expanded=True):
    st.write("La probabilidad es una **estimación estadística** de llegar 15 minutos o más tarde, condicionada a que el vuelo opere y no sea desviado. No predice cancelaciones. Utiliza ruta, aerolínea, horario, duración y tasas históricas disponibles al corte simulado.")
with st.expander("Limitaciones del modelo y calidad de los datos", expanded=True):
    st.warning("**Atención:** en la evaluación de 2026, el modelo original subestimó considerablemente el riesgo medio de SFO → LAX. Las probabilidades no deben interpretarse como perfectamente calibradas.")
    st.write(f"El desfase de publicación de {LAG} días es un **supuesto del proyecto**. Los datos históricos llegan hasta {config['ultima_fecha_historica']} y no se actualizan automáticamente.")
    st.caption("No se consultan vuelos comerciales ni horarios en tiempo real. Ingresa opciones reales de una aerolínea o buscador. Solo se admiten anticipaciones de 30, 60, 90 y 180 días.")
