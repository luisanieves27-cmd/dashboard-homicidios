import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- Page config ----------------
st.set_page_config(page_title="Tablero de Homicidios - Pro", layout="wide")

# ---------------- Load & clean data ----------------
df = pd.read_excel("homicidio.xlsx")

# normalize column names
df.columns = df.columns.str.strip()

# normalize string columns (avoid case/space mismatches)
str_cols = ["DEPARTAMENTO", "MUNICIPIO", "GENERO", "ARMA MEDIO", "*AGRUPA_EDAD_PERSONA"]
for c in str_cols:
    if c in df.columns:
        df[c] = df[c].astype(str).str.strip().str.upper()

# ensure CANTIDAD numeric
if "CANTIDAD" in df.columns:
    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(0).astype(int)
else:
    st.error("La columna 'CANTIDAD' no existe en el Excel. Revisar nombres de columnas.")
    st.stop()

# process dates and derived columns
if "FECHA HECHO" in df.columns:
    df["FECHA HECHO"] = pd.to_datetime(df["FECHA HECHO"], errors="coerce")
    df["AÑO"] = df["FECHA HECHO"].dt.year
    df["MES_NUM"] = df["FECHA HECHO"].dt.month
    df["MES"] = df["FECHA HECHO"].dt.month_name(locale='es_ES')
else:
    st.error("La columna 'FECHA HECHO' no existe en el Excel. Revisar nombres de columnas.")
    st.stop()

# helper
def fmt(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except:
        return str(n)

# ---------------- UI: Title + sidebar filters ----------------
azul = "#0055A4"
st.markdown(f"<h1 style='color:{azul};'>📊 Tablero de Homicidios - Informe académico</h1>", unsafe_allow_html=True)
st.markdown("Filtros globales (afectan los gráficos y los cálculos del informe).")

st.sidebar.header("Filtros globales")
anios = sorted(df["AÑO"].dropna().unique().astype(int).tolist())
anios_default = anios if anios else [datetime.now().year]
anio_sel = st.sidebar.multiselect("Año(s)", anios_default, default=anios_default)
depto_global = st.sidebar.multiselect("Departamento(s) (filtro global, opcional)", sorted(df["DEPARTAMENTO"].dropna().unique()), default=sorted(df["DEPARTAMENTO"].dropna().unique()))

df_global = df[(df["AÑO"].isin(anio_sel)) & (df["DEPARTAMENTO"].isin(depto_global))]

# ---------------- Existing tabs (kept simple) ----------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Tendencias", "📊 Comparativos", "📍 Municipios", "📝 Tareas/Informe"])

with tab1:
    st.subheader("Evolución de homicidios por año (global según filtros)")
    fig1 = px.histogram(df_global, x="AÑO", y="CANTIDAD", histfunc="sum", title="Total de homicidios por año", color_discrete_sequence=[azul])
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Comparativos rápidos")
    if "GENERO" in df_global.columns:
        figg = px.pie(df_global.groupby("GENERO")["CANTIDAD"].sum().reset_index(), names="GENERO", values="CANTIDAD", title="Distribución por género", color_discrete_sequence=[azul, "#3399FF"])
        st.plotly_chart(figg, use_container_width=True)
    else:
        st.info("No hay columna 'GENERO' para comparar.")

with tab3:
    st.subheader("Top municipios (según filtros globales)")
    top_mun = df_global.groupby("MUNICIPIO")["CANTIDAD"].sum().reset_index().sort_values(by="CANTIDAD", ascending=False).head(15)
    st.plotly_chart(px.bar(top_mun, x="MUNICIPIO", y="CANTIDAD", title="Top municipios", color="CANTIDAD", color_continuous_scale="Blues"), use_container_width=True)
    st.dataframe(top_mun)

# ---------------- Tareas/Informe (respuestas automáticas para tu trabajo) ----------------
with tab4:
    st.header("Respuestas automáticas para las 5 preguntas solicitadas")
    st.markdown("Estas respuestas se calculan a partir de la tabla (sin modificarla). Revisa que los nombres de departamento y municipio coincidan exactamente con los del Excel (el código normaliza a mayúsculas).")

    # ------------- 1 -------------
    st.subheader("1) Género más afectado en el municipio con más homicidios (Cundinamarca)")
    depto = "CUNDINAMARCA"
    df_dep = df[df["DEPARTAMENTO"] == depto]
    if df_dep.empty:
        st.write(f"No hay registros para el departamento {depto}.")
    else:
        # municipio con más homicidios
        mun_max = df_dep.groupby("MUNICIPIO")["CANTIDAD"].sum().idxmax()
        mun_val = int(df_dep.groupby("MUNICIPIO")["CANTIDAD"].sum().max())
        # genero mas afectado en ese municipio
        df_mun = df_dep[df_dep["MUNICIPIO"] == mun_max]
        genero_top = df_mun.groupby("GENERO")["CANTIDAD"].sum().idxmax()
        genero_val = int(df_mun.groupby("GENERO")["CANTIDAD"].sum().max())

        st.markdown(f"**Municipio seleccionado:** {mun_max.title()}  \n**Total homicidios en ese municipio:** {fmt(mun_val)}  ")
        st.markdown(f"**Género más afectado:** {genero_top.title()} con **{fmt(genero_val)}** casos.")

        # sugerencia preventiva (plantilla)
        suger1 = (
            f"Recomendación: Implementar campañas de prevención y protección focalizadas al grupo {genero_top.title()} en {mun_max.title()}. "
            "Acciones concretas: programas de intervención comunitaria, puntos de atención y apoyo psicológico, instalación de iluminación pública en puntos críticos, y desarrollo de estrategias de prevención situacional (patrullaje orientado a horarios críticos)."
        )
        st.markdown("**Estrategia preventiva sugerida (puedes ajustar para justificar hasta 1 punto):**")
        st.write(suger1)

    st.markdown("---")

    # ------------- 2 -------------
    st.subheader("2) Arma más utilizada contra víctimas masculinas (Valle del Cauca)")
    depto2 = "VALLE DEL CAUCA".upper()
    df_dep2 = df[df["DEPARTAMENTO"] == depto2]
    if df_dep2.empty:
        st.write(f"No hay registros para el departamento {depto2}.")
    else:
        mun_max2 = df_dep2.groupby("MUNICIPIO")["CANTIDAD"].sum().idxmax()
        mun_val2 = int(df_dep2.groupby("MUNICIPIO")["CANTIDAD"].sum().max())
        df_mun2 = df_dep2[(df_dep2["MUNICIPIO"] == mun_max2) & (df_dep2["GENERO"] == "MASCULINO")]
        if df_mun2.empty:
            st.write(f"No hay registros de víctimas masculinas en {mun_max2.title()}.")
        else:
            arma_top = df_mun2.groupby("ARMA MEDIO")["CANTIDAD"].sum().idxmax()
            arma_val = int(df_mun2.groupby("ARMA MEDIO")["CANTIDAD"].sum().max())
            st.markdown(f"**Municipio seleccionado:** {mun_max2.title()}  \n**Total homicidios en ese municipio:** {fmt(mun_val2)}")
            st.markdown(f"**Arma más usada contra víctimas masculinas:** {arma_top.title()} con **{fmt(arma_val)}** casos.")

            accion = (
                f"Acción de control policial: reforzar controles y registros en puntos donde se detecte circulación de {arma_top.title()} (operativos de control de porte, revisión de venta/almacenamiento si aplica, puestos de control en horarios críticos). "
                "Además, implementar inteligencia focalizada sobre redes de suministro local del arma y operativos de desarme voluntario o coercitivo según la legislación local."
            )
            st.markdown("**Acción de control sugerida (justificada):**")
            st.write(accion)

    st.markdown("---")

    # ------------- 3 -------------
    st.subheader("3) Mes crítico en 2024 (Antioquia)")
    depto3 = "ANTIOQUIA"
    df_dep3 = df[(df["DEPARTAMENTO"] == depto3) & (df["AÑO"] == 2024)]
    if df_dep3.empty:
        st.write(f"No hay registros de 2024 para {depto3}.")
    else:
        mes_group = df_dep3.groupby("MES_NUM")["CANTIDAD"].sum().reset_index()
        if mes_group.empty:
            st.write("No hay datos mensuales.")
        else:
            mes_max_row = mes_group.loc[mes_group["CANTIDAD"].idxmax()]
            mes_num = int(mes_max_row["MES_NUM"])
            mes_name = pd.to_datetime(mes_num, format="%m").strftime("%B").capitalize()
            mes_val = int(mes_max_row["CANTIDAD"])
            st.markdown(f"**Mes crítico en 2024:** {mes_name} con **{fmt(mes_val)}** homicidios.")

            operativo = (
                f"Operativo recomendado: intensificar operativos preventivos y de control policial en {mes_name} (por ejemplo: patrullajes focalizados en zonas críticas, operativos de interdicción nocturna y despliegue de unidades tácticas en horarios pico). "
                "Además, coordinar con programas de prevención social y fortalecer rutas de denuncia durante ese periodo."
            )
            st.markdown("**Operativo sugerido:**")
            st.write(operativo)

    st.markdown("---")

    # ------------- 4 -------------
    st.subheader("4) Comparación intermunicipal (Atlántico): Barranquilla vs Soledad")
    depto4 = "ATLÁNTICO"
    df_dep4 = df[df["DEPARTAMENTO"] == depto4]
    if df_dep4.empty:
        st.write(f"No hay registros para {depto4}.")
    else:
        munA = "BARRANQUILLA"
        munB = "SOLEDAD"
        valA = int(df_dep4[df_dep4["MUNICIPIO"] == munA]["CANTIDAD"].sum())
        valB = int(df_dep4[df_dep4["MUNICIPIO"] == munB]["CANTIDAD"].sum())
        diferencia = abs(valA - valB)
        mayor = munA if valA > valB else (munB if valB > valA else "Empate")
        st.markdown(f"**Barranquilla:** {fmt(valA)} homicidios  \n**Soledad:** {fmt(valB)} homicidios  \n**Diferencia:** {fmt(diferencia)}")
        st.markdown(f"**Más casos:** {mayor.title() if mayor!='Empate' else 'Empate'}")

        justif = (
            "Justificación para mayor atención investigativa: analizar contexto del municipio con mayor cifra (puntos calientes, redes criminales identificadas, concentración espacial de eventos, reincidencia en zonas específicas). "
            "Se sugiere priorizar el municipio con mayor número de casos para despliegues de unidades investigativas, análisis criminológico y acciones de prevención situacional."
        )
        st.markdown("**Justificación de atención investigativa (sugerida):**")
        st.write(justif)

    st.markdown("---")

    # ------------- 5 -------------
    st.subheader("5) Perfil víctima–arma (Santander)")
    depto5 = "SANTANDER"
    df_dep5 = df[df["DEPARTAMENTO"] == depto5]
    if df_dep5.empty:
        st.write(f"No hay registros para {depto5}.")
    else:
        mun_max5 = df_dep5.groupby("MUNICIPIO")["CANTIDAD"].sum().idxmax()
        df_target = df_dep5[(df_dep5["MUNICIPIO"] == mun_max5) & (df_dep5["GENERO"] == "FEMENINO")]
        if df_target.empty:
            st.markdown(f"En {mun_max5.title()} no se registran homicidios con víctimas femeninas en los datos disponibles.")
        else:
            arma_top5 = df_target.groupby("ARMA MEDIO")["CANTIDAD"].sum().idxmax()
            arma_val5 = int(df_target.groupby("ARMA MEDIO")["CANTIDAD"].sum().max())
            st.markdown(f"**Municipio seleccionado:** {mun_max5.title()}  \n**Arma más usada contra mujeres:** {arma_top5.title()} con **{fmt(arma_val5)}** casos.")

            suger5 = (
                f"Estrategia preventiva e investigativa: diseñar campañas de protección y medidas específicas dirigidas a mujeres en {mun_max5.title()} (líneas de atención, educación comunitaria sobre riesgos, apoyo psicosocial). "
                f"Investigativamente: priorizar la recolección de evidencia forense y el análisis de redes/relaciones cuando {arma_top5.title()} sea la modalidad predominante; coordinar con unidades de violencia de género y centros de atención."
            )
            st.markdown("**Sugerencia de prevención e investigación:**")
            st.write(suger5)

    st.markdown("---")
    st.info("Puedes usar estos resultados como base para responder puntualmente cada ítem del trabajo (cada bloque incluye municipio, cifra y una recomendación justificable). Si quieres, exporto un PDF o lo formateo en texto listo para pegar en tu entrega.")
