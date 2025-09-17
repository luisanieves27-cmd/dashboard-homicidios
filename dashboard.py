import streamlit as st
import pandas as pd
import plotly.express as px

# ================= Configuración de la página =================
st.set_page_config(page_title="Tablero de Homicidios", layout="wide")

# ================= Cargar y preparar datos =================
df = pd.read_excel("homicidio.xlsx")

# Limpiar nombres de columnas (quita espacios invisibles, mayúsculas/minúsculas)
df.columns = df.columns.str.strip()

# Procesar fechas
df["FECHA HECHO"] = pd.to_datetime(df["FECHA HECHO"], errors="coerce")

# Crear columnas de año y mes en español
meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
df["AÑO"] = df["FECHA HECHO"].dt.year
df["MES"] = df["FECHA HECHO"].dt.month.map(meses_es)

# Paleta de azules
azul1 = "#003366"
azul2 = "#0055A4"
azul3 = "#0077CC"
azul4 = "#3399FF"

# ================= Título =================
st.markdown(f"<h1 style='color:{azul2};'>📊 Tablero de Homicidios en Colombia</h1>", unsafe_allow_html=True)
st.markdown("Análisis interactivo de los homicidios registrados en la base de datos oficial.")

# ================= Filtros =================
st.sidebar.header("Filtros")
anios = sorted(df["AÑO"].dropna().unique())
departamentos = sorted(df["DEPARTAMENTO"].dropna().unique())

anio_sel = st.sidebar.multiselect("Selecciona el año", anios, default=anios)
depto_sel = st.sidebar.multiselect("Selecciona el departamento", departamentos, default=departamentos)

# Aplicar filtros
df_filtrado = df[(df["AÑO"].isin(anio_sel)) & (df["DEPARTAMENTO"].isin(depto_sel))]

# ================= KPI's =================
st.subheader("🔎 Indicadores principales")

total_homicidios = int(df_filtrado["CANTIDAD"].sum())
total_masculino = int(df_filtrado[df_filtrado["GENERO"] == "MASCULINO"]["CANTIDAD"].sum())
total_femenino = int(df_filtrado[df_filtrado["GENERO"] == "FEMENINO"]["CANTIDAD"].sum())

mun_top = df_filtrado.groupby("MUNICIPIO")["CANTIDAD"].sum().idxmax() if not df_filtrado.empty else "N/A"
depto_top = df_filtrado.groupby("DEPARTAMENTO")["CANTIDAD"].sum().idxmax() if not df_filtrado.empty else "N/A"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total homicidios", f"{total_homicidios:,}")
col2.metric("Hombres", f"{total_masculino:,}")
col3.metric("Mujeres", f"{total_femenino:,}")
col4.metric("Municipio crítico", mun_top)
col5.metric("Departamento crítico", depto_top)

st.markdown("---")

# ================= Pestañas =================
tab1, tab2, tab3 = st.tabs(["📈 Tendencias", "📊 Comparativos", "📍 Municipios"])

# 📈 Tendencias
with tab1:
    st.subheader("Evolución de homicidios por año")
    fig1 = px.histogram(df_filtrado, x="AÑO", y="CANTIDAD",
                        histfunc="sum",
                        title="Total de homicidios por año",
                        color_discrete_sequence=[azul2])
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Homicidios por mes")
    fig2 = px.histogram(df_filtrado, x="MES", y="CANTIDAD",
                        histfunc="sum",
                        title="Distribución mensual de homicidios",
                        category_orders={"MES": list(meses_es.values())},
                        color_discrete_sequence=[azul3])
    st.plotly_chart(fig2, use_container_width=True)

# 📊 Comparativos
with tab2:
    st.subheader("Homicidios por género")
    fig3 = px.pie(df_filtrado, values="CANTIDAD", names="GENERO",
                  title="Distribución por género",
                  color_discrete_sequence=[azul2, azul4])
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Homicidios por grupo de edad")
    fig4 = px.bar(df_filtrado, x="*AGRUPA_EDAD_PERSONA", y="CANTIDAD",
                  title="Comparación por grupo de edad",
                  color="*AGRUPA_EDAD_PERSONA",
                  color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Armas más usadas")
    fig5 = px.bar(df_filtrado, x="ARMA MEDIO", y="CANTIDAD",
                  title="Distribución por tipo de arma",
                  color="ARMA MEDIO",
                  color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig5, use_container_width=True)

# 📍 Municipios
with tab3:
    st.subheader("Top municipios con más homicidios")
    top_mun = df_filtrado.groupby("MUNICIPIO")["CANTIDAD"].sum().reset_index().sort_values(by="CANTIDAD", ascending=False).head(10)
    fig6 = px.bar(top_mun, x="MUNICIPIO", y="CANTIDAD",
                  title="10 municipios con mayor cantidad de homicidios",
                  color="CANTIDAD",
                  color_continuous_scale="Blues")
    st.plotly_chart(fig6, use_container_width=True)

    st.dataframe(top_mun)
# 📑 Respuestas al trabajo

with tab4:
    st.subheader("📑 Respuestas automáticas a las preguntas (con soporte gráfico)")

    # 1. Género más afectado en municipio top de Cundinamarca
    df_cund = df[df["DEPARTAMENTO"] == "CUNDINAMARCA"]
    top_mun_cund = df_cund.groupby("MUNICIPIO")["CANTIDAD"].sum().idxmax()
    df_cund_mun = df_cund[df_cund["MUNICIPIO"] == top_mun_cund]
    top_gen_cund = df_cund_mun.groupby("GENERO")["CANTIDAD"].sum().idxmax()
    casos_cund = df_cund_mun.groupby("GENERO")["CANTIDAD"].sum().max()
    st.markdown(f"**1.** En Cundinamarca, el municipio con más homicidios es **{top_mun_cund}**. "
                f"El género más afectado fue **{top_gen_cund}** con **{casos_cund} casos**.")
    fig_q1 = px.bar(df_cund_mun, x="GENERO", y="CANTIDAD",
                    title=f"Género más afectado en {top_mun_cund} (Cundinamarca)",
                    color="GENERO",
                    color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig_q1, use_container_width=True)

    # 2. Arma más usada en víctimas masculinas en Valle del Cauca
    df_valle = df[df["DEPARTAMENTO"] == "VALLE DEL CAUCA"]
    top_mun_valle = df_valle.groupby("MUNICIPIO")["CANTIDAD"].sum().idxmax()
    df_valle_masc = df_valle[(df_valle["MUNICIPIO"] == top_mun_valle) & (df_valle["GENERO"] == "MASCULINO")]
    arma_valle = df_valle_masc.groupby("ARMA MEDIO")["CANTIDAD"].sum().idxmax()
    casos_valle = df_valle_masc.groupby("ARMA MEDIO")["CANTIDAD"].sum().max()
    st.markdown(f"**2.** En Valle del Cauca, el municipio con más homicidios es **{top_mun_valle}**. "
                f"El arma más usada contra hombres fue **{arma_valle}** con **{casos_valle} casos**.")
    fig_q2 = px.bar(df_valle_masc, x="ARMA MEDIO", y="CANTIDAD",
                    title=f"Armas usadas contra hombres en {top_mun_valle} (Valle del Cauca)",
                    color="ARMA MEDIO",
                    color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig_q2, use_container_width=True)

    # 3. Mes crítico en Antioquia en 2024
    df_ant = df[(df["DEPARTAMENTO"] == "ANTIOQUIA") & (df["AÑO"] == 2024)]
    mes_ant = df_ant.groupby("MES")["CANTIDAD"].sum().idxmax()
    casos_ant = df_ant.groupby("MES")["CANTIDAD"].sum().max()
    st.markdown(f"**3.** En Antioquia, el mes más crítico de 2024 fue **{mes_ant}** con **{casos_ant} casos**.")
    fig_q3 = px.bar(df_ant, x="MES", y="CANTIDAD",
                    title="Homicidios por mes en Antioquia (2024)",
                    color="MES",
                    color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig_q3, use_container_width=True)

    # 4. Comparación Barranquilla vs Soledad en Atlántico
    df_atl = df[df["DEPARTAMENTO"] == "ATLÁNTICO"]
    casos_barr = df_atl[df_atl["MUNICIPIO"] == "BARRANQUILLA"]["CANTIDAD"].sum()
    casos_sol = df_atl[df_atl["MUNICIPIO"] == "SOLEDAD"]["CANTIDAD"].sum()
    muni_mayor = "BARRANQUILLA" if casos_barr > casos_sol else "SOLEDAD"
    dif = abs(casos_barr - casos_sol)
    st.markdown(f"**4.** En Atlántico: Barranquilla tuvo **{casos_barr} casos**, Soledad tuvo **{casos_sol} casos**. "
                f"El municipio con más homicidios fue **{muni_mayor}**, con una diferencia de **{dif} casos**.")
    df_comp = pd.DataFrame({
        "Municipio": ["BARRANQUILLA", "SOLEDAD"],
        "Casos": [casos_barr, casos_sol]
    })
    fig_q4 = px.bar(df_comp, x="Municipio", y="Casos",
                    title="Comparación: Barranquilla vs Soledad (Atlántico)",
                    color="Municipio",
                    color_discrete_sequence=[azul2, azul4])
    st.plotly_chart(fig_q4, use_container_width=True)

    # 5. Arma más usada contra mujeres en Santander
    df_sant = df[df["DEPARTAMENTO"] == "SANTANDER"]
    top_mun_sant = df_sant.groupby("MUNICIPIO")["CANTIDAD"].sum().idxmax()
    df_sant_fem = df_sant[(df_sant["MUNICIPIO"] == top_mun_sant) & (df_sant["GENERO"] == "FEMENINO")]
    arma_sant = df_sant_fem.groupby("ARMA MEDIO")["CANTIDAD"].sum().idxmax()
    casos_sant = df_sant_fem.groupby("ARMA MEDIO")["CANTIDAD"].sum().max()
    st.markdown(f"**5.** En Santander, el municipio con más homicidios es **{top_mun_sant}**. "
                f"El arma más usada contra mujeres fue **{arma_sant}** con **{casos_sant} casos**.")
    fig_q5 = px.bar(df_sant_fem, x="ARMA MEDIO", y="CANTIDAD",
                    title=f"Armas usadas contra mujeres en {top_mun_sant} (Santander)",
                    color="ARMA MEDIO",
                    color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig_q5, use_container_width=True)
