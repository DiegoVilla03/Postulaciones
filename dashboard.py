import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard de Postulaciones", layout="wide")

st.title("Seguimiento de Postulaciones de Empleo")

EXCEL_FILE = r"data\Postulaciones.xlsx"

if not Path(EXCEL_FILE).exists():
    st.error(f"No se encontró el archivo `{EXCEL_FILE}` en el directorio actual.")
    st.stop()

df = pd.read_excel(EXCEL_FILE)

# Normalización básica
df["Estatus"] = df["Estatus"].fillna("Sin especificar")
df["Modalidad"] = df["Modalidad"].fillna("No especificada")
df["Tipo de empresa"] = df["Tipo de empresa"].fillna("No especificada")

def binarizar_columna(df, col):
    """
    Convierte una columna de texto ('Sí' / 'No' / NaN / vacío) en binario (1 / 0)
    """
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.lower()
            .str.strip()
            .replace({"no": 0, "nan": 0, "": 0})
            .apply(lambda x: 1 if x not in [0, "0"] else 0)
        )
    else:
        df[col] = 0
    return df

df = binarizar_columna(df, "CV Visto")
df = binarizar_columna(df, "Entrevista")


st.header("Resumen general")

col1, col2, col3, col4, col5 = st.columns(5)
total_post = len(df)
empresas_unicas = df["Empresa"].nunique() if "Empresa" in df.columns else None
cv_visto = df["CV Visto"].mean() * 100
entrevistas = df["Entrevista"].mean() * 100
estatus_mas_comun = df["Estatus"].mode()[0]

col1.metric("Total postulaciones", total_post)
col2.metric("Empresas únicas", empresas_unicas)
col3.metric("% CV Vistos", f"{cv_visto:.1f}%")
col4.metric("% Entrevistas", f"{entrevistas:.1f}%")
col5.metric("Estatus más frecuente", estatus_mas_comun)


st.header("Visualizaciones")

# --- Por tipo de empresa ---
st.subheader("Distribución por tipo de empresa")
tipo_counts = df["Tipo de empresa"].value_counts().reset_index()
tipo_counts.columns = ["Tipo de empresa", "Cantidad"]
fig_tipo = px.bar(
    tipo_counts,
    x="Tipo de empresa",
    y="Cantidad",
    text="Cantidad",
    color="Cantidad",
    color_continuous_scale="algae",
)
fig_tipo.update_layout(xaxis_title=None, yaxis_title="Cantidad", height=400)
st.plotly_chart(fig_tipo, use_container_width=True)

st.header("Distribución por categoría de puesto")

categoria_counts = df["Puesto"].value_counts().reset_index()
categoria_counts.columns = ["Categoría", "Cantidad"]

fig = px.bar(
    categoria_counts.sort_values("Cantidad", ascending=True),  
    x="Cantidad",
    y="Categoría",
    orientation="h",
    text="Cantidad",
    color="Cantidad",
    color_continuous_scale="algae",
)

fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis_title="Cantidad",
    yaxis_title=None,
    height=500,
    showlegend=False,
    margin=dict(l=80, r=40, t=40, b=40)
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Distribución por estatus de las postulaciones")
estatus_counts = df["Estatus"].value_counts().reset_index()
estatus_counts.columns = ["Estatus", "Cantidad"]
fig_estatus = px.pie(
    estatus_counts,
    names="Estatus",
    values="Cantidad",
    hole=0.4,
    color_discrete_sequence=px.colors.sequential.algae,
)
st.plotly_chart(fig_estatus, use_container_width=True)

fecha_col = None
for col in df.columns:
    if "fecha" in col.lower():
        fecha_col = col
        break

st.subheader("Tendencia temporal de postulaciones")
if fecha_col:
    df[fecha_col] = pd.to_datetime(df[fecha_col], errors="coerce")
    if df[fecha_col].notna().any():
        df_fecha = df.groupby(df[fecha_col].dt.to_period("W")).size().reset_index(name="Postulaciones")
        df_fecha[fecha_col] = df_fecha[fecha_col].dt.start_time
        fig3 = px.line(df_fecha, x=fecha_col, y="Postulaciones", markers=True, color_discrete_sequence=px.colors.sequential.algae)
        fig3.update_layout(height=400, xaxis_title="Fecha", yaxis_title="Postulaciones")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No hay fechas válidas para graficar.")
else:
    st.warning("No se encontró ninguna columna que contenga 'Fecha'.")
