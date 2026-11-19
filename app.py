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

/* Flight Delay Risk: superficies claras y texto oscuro en el contenido;
   encabezado y barra lateral azul marino, sin depender del modo del teléfono. */
:root {
  --fd-navy:#10263F;
  --fd-blue:#0B4FA3;
  --fd-teal:#007F86;
  --fd-coral:#ED795B;
  --fd-muted:#5A6E83;
  --fd-background:#F5F8FC;
  --fd-border:#D7E3EE;
}
[data-testid="stAppViewContainer"] { background-color:var(--fd-background) !important; }
[data-testid="stMain"] { color:var(--fd-navy); }
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] > p,
[data-testid="stMain"] [data-testid="stExpanderDetails"] p,
[data-testid="stMain"] [data-testid="stExpanderDetails"] li {color:var(--fd-navy) !important;}
[data-testid="stMain"] [data-testid="stCaptionContainer"] p,
[data-testid="stMain"] [data-testid="stCaptionContainer"] span {color:var(--fd-muted) !important;opacity:1;}
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stWidgetLabel"] label {color:var(--fd-navy) !important;font-weight:700 !important;opacity:1;}
h1,h2,h3,h4 {font-family:'Manrope',sans-serif !important;letter-spacing:-.035em;}
h2 {font-size:1.45rem !important;}
.block-container {max-width:1330px;padding-top:1.8rem;padding-bottom:3rem;}

/* Barra lateral: oscura, con selector de fecha claro y legible. */
[data-testid="stSidebar"] {background-color:var(--fd-navy) !important;}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#F3F7FA !important;opacity:1 !important;}
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-baseweb="base-input"],
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
  background-color:#FFFFFF !important;
  color:var(--fd-navy) !important;
  -webkit-text-fill-color:var(--fd-navy) !important;
  opacity:1 !important;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] svg {color:var(--fd-navy) !important;fill:var(--fd-navy) !important;}

/* Cabecera editorial, con sus propios colores, no heredados del tema. */
.hero {
  background:linear-gradient(115deg,#10263F 0%,#16415A 66%,#007F86 130%);
  border-radius:22px;padding:33px 38px;margin-bottom:25px;color:#FFFFFF;
  box-shadow:0 12px 28px #10263F16;
  font-family:'DM Sans',sans-serif;
}
.hero .eyebrow {color:#9AE1DE;font-weight:800;font-size:.73rem;letter-spacing:.18em;}
[data-testid="stMain"] .hero h1 {font-size:clamp(2rem,4vw,3.25rem);line-height:1.12;margin:10px 0 12px;color:#FFFFFF !important;}
[data-testid="stMain"] .hero p {color:#E1EDF2 !important;font-size:1.05rem;max-width:770px;margin:0;}
.hero .pills {display:flex;gap:9px;flex-wrap:wrap;margin-top:20px;}
.hero .pill {background:#FFFFFF18;border:1px solid #FFFFFF30;border-radius:100px;padding:7px 12px;font-size:.8rem;color:#EAF8FA;}
.section-kicker {font-size:.73rem;font-weight:800;letter-spacing:.15em;color:var(--fd-teal);margin-bottom:4px;}
.metric-card {background:#FFFFFF;border:1px solid #E3EAF1;border-radius:17px;padding:20px 23px;min-height:126px;box-shadow:0 4px 18px #12294208;}
.metric-card .label {font-size:.8rem;color:#52667C;font-weight:700;letter-spacing:.02em;}
.metric-card .value {font-family:'Manrope',sans-serif;font-size:1.85rem;font-weight:800;color:var(--fd-navy);margin-top:8px;}
.metric-card .detail {font-size:.78rem;color:#587087;margin-top:2px;}
.note {background:#ECF8F7;border:1px solid #BCE8E2;border-left:4px solid var(--fd-teal);border-radius:13px;padding:17px 19px;color:#183D48;}
.note strong {color:#006D73;}
.note .small-muted {color:#526A78 !important;font-size:.83rem;}

/* Formulario: nunca hacer texto claro sobre campos claros. */
[data-testid="stMain"] div[data-testid="stForm"] {
  background-color:#FFFFFF !important;
  color:var(--fd-navy) !important;
  border:1px solid #E1E9F0;border-radius:19px;padding:22px 24px;
  box-shadow:0 5px 24px #10263F08;
}
[data-testid="stMain"] [data-baseweb="select"] > div,
[data-testid="stMain"] [data-baseweb="input"] > div,
[data-testid="stMain"] [data-baseweb="base-input"],
[data-testid="stMain"] [data-testid="stTimeInput"] [data-baseweb="input"] > div,
[data-testid="stMain"] [data-testid="stNumberInput"] [data-baseweb="input"] > div {
  background-color:#FFFFFF !important;
  border-color:#CAD9E6 !important;
  color:var(--fd-navy) !important;
}
[data-testid="stMain"] [data-baseweb="select"] > div *,
[data-testid="stMain"] [data-baseweb="select"] input,
[data-testid="stMain"] [data-baseweb="input"] input,
[data-testid="stMain"] [data-testid="stNumberInput"] input,
[data-testid="stMain"] [data-testid="stTimeInput"] input {
  color:var(--fd-navy) !important;
  -webkit-text-fill-color:var(--fd-navy) !important;
  opacity:1 !important;
}
[data-testid="stMain"] [data-baseweb="select"] svg,
[data-testid="stMain"] [data-testid="stNumberInput"] button svg {
  color:#38546B !important;
  fill:#38546B !important;
}
/* Los desplegables de BaseWeb suelen renderizarse fuera del formulario. */
[data-baseweb="popover"] [role="listbox"] {
  background-color:#FFFFFF !important;color:var(--fd-navy) !important;
}
[data-baseweb="popover"] [role="option"] {color:var(--fd-navy) !important;}
[data-baseweb="popover"] [role="option"]:hover {background-color:#EAF4F8 !important;}

/* Sustitutos accesibles de los antiguos inputs deshabilitados. */
.fd-readonly {margin-bottom:12px;}
.fd-readonly-label {display:block;font-size:.89rem;font-weight:700;color:var(--fd-navy);margin-bottom:7px;}
.fd-readonly-value {
  display:flex;align-items:center;min-height:43px;width:100%;padding:10px 13px;
  background:#EAF2F7;color:var(--fd-navy);border:1px solid #C6D9E6;
  border-radius:10px;font-size:1rem;font-weight:600;line-height:1.3;
}

/* Botones: el texto siempre contrasta en claro y oscuro. */
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button {
  background-color:var(--fd-teal) !important;
  border:1px solid var(--fd-teal) !important;
  border-radius:11px !important;
  font-weight:700 !important;
  color:#FFFFFF !important;
  min-height:44px;
}
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button:hover {
  background-color:#00676E !important;border-color:#00676E !important;
}
[data-testid="stMain"] [data-testid="stButton"] button {
  background-color:var(--fd-navy) !important;
  border:1px solid var(--fd-navy) !important;
  border-radius:11px !important;
  color:#FFFFFF !important;
  font-weight:700 !important;
  min-height:44px;
}
[data-testid="stMain"] [data-testid="stButton"] button:hover {
  background-color:#214B72 !important;border-color:#214B72 !important;
}
[data-testid="stMain"] [data-testid="stFormSubmitButton"] button *,
[data-testid="stMain"] [data-testid="stButton"] button * {
  color:#FFFFFF !important;-webkit-text-fill-color:#FFFFFF !important;
}
[data-testid="stMain"] button:focus-visible {outline:3px solid #49BDCE !important;outline-offset:3px;}

/* Avisos propios: colores legibles sin depender de st.success/st.warning ni del SO. */
.fd-notice {display:flex;align-items:flex-start;gap:12px;padding:14px 16px;
  border-radius:13px;border:1px solid;margin:12px 0;font-family:'DM Sans',sans-serif;
  line-height:1.5;font-size:.92rem;}
.fd-notice .fd-symbol {display:inline-flex;align-items:center;justify-content:center;
  width:24px;height:24px;flex:0 0 24px;border-radius:50%;font-weight:800;font-size:14px;}
.fd-notice .fd-message {flex:1;color:inherit !important;overflow-wrap:anywhere;}
.fd-notice-success {background:#E4F7EE;color:#18583C;border-color:#A7DCC6;}
.fd-notice-success .fd-symbol {color:#FFFFFF;background:#197A57;}
.fd-notice-info {background:#E8F3FB;color:#194665;border-color:#AED0EB;}
.fd-notice-info .fd-symbol {color:#FFFFFF;background:#1B6F9F;}
.fd-notice-warning {background:#FFF0DD;color:#74400D;border-color:#F3CD9B;}
.fd-notice-warning .fd-symbol {color:#FFFFFF;background:#A65C18;}
.fd-notice-error {background:#FFE9E9;color:#86292B;border-color:#F3B8B9;}
.fd-notice-error .fd-symbol {color:#FFFFFF;background:#B23E43;}

/* Expansores: título y contenido explícitos, texto azul sobre blanco. */
[data-testid="stMain"] [data-testid="stExpander"] {
  background:#FFFFFF !important;border:1px solid #DCE7EE !important;
  border-radius:13px !important;overflow:hidden;margin-bottom:12px;
}
[data-testid="stMain"] [data-testid="stExpander"] summary {
  background:#EAF2F6 !important;color:var(--fd-navy) !important;
}
[data-testid="stMain"] [data-testid="stExpander"] summary p,
[data-testid="stMain"] [data-testid="stExpander"] summary span,
[data-testid="stMain"] [data-testid="stExpander"] summary svg {
  color:var(--fd-navy) !important;fill:var(--fd-navy) !important;font-weight:700 !important;
}
[data-testid="stMain"] [data-testid="stExpanderDetails"] {
  background:#FFFFFF !important;color:var(--fd-navy) !important;padding:12px 17px;
}
[data-testid="stDataFrame"] {border-radius:14px;overflow:hidden;}

@media (max-width:640px) {
  .block-container {padding:1rem .85rem 2.2rem;}
  .hero {padding:23px 20px;border-radius:18px;}
  [data-testid="stMain"] .hero h1 {font-size:2.15rem !important;}
  [data-testid="stMain"] div[data-testid="stForm"] {padding:17px 14px;}
  .metric-card {min-height:105px;padding:16px 18px;}
  .fd-notice {padding:12px 13px;font-size:.88rem;}
}
</style>
""", unsafe_allow_html=True)


def notice(kind, message):
    """Muestra un mensaje legible con el mismo contraste en móvil y escritorio."""
    symbols = {"success": "✓", "info": "i", "warning": "!", "error": "×"}
    if kind not in symbols:
        raise ValueError("Tipo de aviso no admitido")
    role = "alert" if kind in {"error", "warning"} else "status"
    st.markdown(
        f'<div class="fd-notice fd-notice-{kind}" role="{role}">'
        f'<span class="fd-symbol" aria-hidden="true">{symbols[kind]}</span>'
        f'<span class="fd-message">{html.escape(str(message))}</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def readonly_field(label, value):
    """Reemplazo visible y accesible para campos deshabilitados."""
    st.markdown(
        '<div class="fd-readonly">'
        f'<span class="fd-readonly-label">{html.escape(str(label))}</span>'
        f'<div class="fd-readonly-value">{html.escape(str(value))}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

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
        readonly_field("Aeropuerto de destino", "LAX — Los Ángeles")
        horizon = st.selectbox("Anticipación de compra (días)", HORIZONS, index=2)
        flight_date = consultation + timedelta(days=int(horizon))
        readonly_field("Fecha del vuelo (calculada)", flight_date.isoformat())
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
            notice("info", "Este vuelo ya está incluido en la comparación. Modifica algún dato para agregar otra opción.")
        else:
            st.session_state.options.append(result)
            notice("success", f"Vuelo agregado · Riesgo estimado: {result['Probabilidad']:.1%}")
    except ValueError as exc:
        notice("error", str(exc))

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
    labels = [f'{r["Ruta"]}  |  {r["Aerolínea"]}  |  {r["Salida"]}' for _, r in df.iterrows()]
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
    notice("info", "Agrega dos o más vuelos para comparar sus riesgos estimados. Puedes comenzar con uno.")

st.markdown('<div class="section-kicker" style="margin-top:32px">03 / CONTEXTO Y LIMITACIONES</div>', unsafe_allow_html=True)
st.subheader("Cómo interpretar los resultados")
st.markdown("Las siguientes notas explican **qué predice el modelo**, qué datos utiliza y cuáles son sus limitaciones. Despliega cada apartado para conocer los detalles.")
with st.expander("¿Qué significa la probabilidad de retraso?", expanded=True):
    st.write("La probabilidad es una **estimación estadística** de llegar 15 minutos o más tarde, condicionada a que el vuelo opere y no sea desviado. No predice cancelaciones. Utiliza ruta, aerolínea, horario, duración y tasas históricas disponibles al corte simulado.")
with st.expander("Limitaciones del modelo y calidad de los datos", expanded=True):
    notice("warning", "Atención: en la evaluación de 2026, el modelo original subestimó considerablemente el riesgo medio de SFO → LAX. Las probabilidades no deben interpretarse como perfectamente calibradas.")
    st.write(f"El desfase de publicación de {LAG} días es un **supuesto del proyecto**. Los datos históricos llegan hasta {config['ultima_fecha_historica']} y no se actualizan automáticamente.")
    st.caption("No se consultan vuelos comerciales ni horarios en tiempo real. Ingresa opciones reales de una aerolínea o buscador. Solo se admiten anticipaciones de 30, 60, 90 y 180 días.")