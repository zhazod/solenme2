import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Configuración de la app
st.set_page_config(
    page_title="Presupuesto Público 2015",
    page_icon=":bar_chart:",
    layout="centered"
)

# Título principal
st.title("📊 Presupuesto Público - Año 2015")
st.markdown("Visualización interactiva por **Partida** y **Subtítulo** del presupuesto público en dólares.")

# Carga de datos desde API oficial
@st.cache_data

def cargar_datos():
    url = "https://datos.gob.cl/api/3/action/datastore_search?resource_id=372b0680-d5f0-4d53-bffa-7997cf6e6512&limit=1000"
    response = requests.get(url)
    if response.status_code == 200:
        records = response.json()['result']['records']
        df = pd.DataFrame(records)
        df['Monto Dolar'] = pd.to_numeric(df['Monto Dolar'], errors='coerce')
        df = df[df['Monto Dolar'] > 0]
        df = df.dropna(subset=['Partida', 'Subtitulo'])
        return df
    else:
        st.error(f"No se pudo acceder a la API: {response.status_code}")
        return pd.DataFrame()

# Cargar y mostrar datos
presupuesto_df = cargar_datos()

st.subheader("Vista previa de registros")
st.dataframe(presupuesto_df.head(10), use_container_width=True)

# Filtro por partida
partidas = sorted(presupuesto_df['Partida'].unique())
partida_sel = st.selectbox("Selecciona una Partida:", partidas)

sub_df = presupuesto_df[presupuesto_df['Partida'] == partida_sel]
resumen = sub_df.groupby('Subtitulo')['Monto Dolar'].sum().reset_index()
resumen = resumen.sort_values(by='Monto Dolar', ascending=False)

# Número de subtítulos a mostrar
st.subheader("Subtítulos con mayor presupuesto (USD)")
top_n = st.slider("Cantidad a mostrar:", 5, min(20, len(resumen)), 10)
resumen_top = resumen.head(top_n)
st.dataframe(resumen_top, use_container_width=True)

# Gráfico
st.subheader("Gráfico de línea del presupuesto por subtítulo")
st.line_chart(resumen_top, x='Subtitulo', y='Monto Dolar')
