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
