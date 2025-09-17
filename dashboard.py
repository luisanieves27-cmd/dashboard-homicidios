import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar los datos
df = pd.read_excel("homicidio.xlsx")

st.title("📊 Tablero de Homicidios")

st.write("Vista general de los datos cargados:")
st.dataframe(df)

# Selección de columna para analizar
columna = st.selectbox("Selecciona una columna para graficar:", df.columns)

# Gráfico de barras
fig = px.histogram(df, x=columna, title=f"Distribución por {columna}")
st.plotly_chart(fig)
