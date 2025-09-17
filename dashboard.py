import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Tablero de Homicidios", layout="wide")

# ================= Cargar y preparar datos =================
df = pd.read_excel("homicidio.xlsx")

# Limpiar nombres de columnas (quita espacios invisibles, mayúsculas/minúsculas)
df.columns = df.columns.str.strip()

# Procesar fechas
df["FECHA HECHO"] = pd.to_datetime(df["FECHA HECHO"], errors="coerce")
df["AÑO"] = df["FECHA HECHO"].dt.year
df["MES"] = df["FECHA HECHO"].dt.month_name()

# Paleta de azules
azul1 = "#003366"
azul2 = "#0055A4"
azul3 = "#0077CC"
azul4 = "#3399FF"

# ================= Título y descripción =================
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
