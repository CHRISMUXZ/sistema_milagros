import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# Configuración general de la app
st.set_page_config(page_title="Sistema Financiero Milagros", layout="wide")
st.title("✨ Sistema Financiero - Tienda Milagros ✨")

# Ruta del archivo Excel y carpeta para imagen
archivo_excel = "registro_milagros.xlsx"
logo_path = "logo_milagros.png"

# Cargar el logo si está disponible
with st.sidebar:
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    st.markdown("## 📂 Menú de Opciones")
    menu = st.radio("", [
        "📅 Registrar Ganancia", "📉 Registrar Gasto", "📊 Resumen",
        "📙 Historial", "📈 Gráfico Línea", "📉 Gráfico Barras"
    ])

# Función para cargar datos
@st.cache_data
def cargar_datos():
    if os.path.exists(archivo_excel):
        return pd.read_excel(archivo_excel)
    else:
        return pd.DataFrame(columns=["Fecha", "Tipo", "Monto", "Descripción"])

# Función para guardar datos
def guardar_datos(df):
    df.to_excel(archivo_excel, index=False)

# Registrar ganancia o gasto
def registrar(tipo):
    st.subheader(f"Registrar {tipo}")
    monto = st.number_input("Monto (S/.)", min_value=0.0, format="%.2f")
    descripcion = st.text_input("Descripción")
    if st.button("Guardar"):
        if monto > 0 and descripcion:
            nueva_fila = pd.DataFrame({
                "Fecha": [datetime.now()],
                "Tipo": [tipo],
                "Monto": [monto],
                "Descripción": [descripcion]
            })
            df = cargar_datos()
            df = pd.concat([df, nueva_fila], ignore_index=True)
            guardar_datos(df)
            st.success(f"{tipo} registrada correctamente")
        else:
            st.error("Por favor, completa todos los campos")

# Mostrar resumen
def mostrar_resumen():
    df = cargar_datos()
    if df.empty:
        st.info("No hay datos disponibles")
        return
    total_ganancia = df[df["Tipo"] == "Ganancia"]["Monto"].sum()
    total_gasto = df[df["Tipo"] == "Gasto"]["Monto"].sum()
    st.metric("Total Ganancias", f"S/. {total_ganancia:.2f}")
    st.metric("Total Gastos", f"S/. {total_gasto:.2f}")
    st.metric("Ganancia Neta", f"S/. {(total_ganancia - total_gasto):.2f}")

    if st.button("📥 Exportar a Excel"):
        st.download_button("Descargar Excel", df.to_csv(index=False).encode('utf-8'),
                           file_name="milagros_exportacion.csv", mime="text/csv")

# Historial
def mostrar_historial():
    df = cargar_datos()
    if df.empty:
        st.info("No hay datos disponibles")
    else:
        st.dataframe(df.sort_values(by="Fecha", ascending=False))

# Gráfico línea
def grafico_linea():
    df = cargar_datos()
    if df.empty:
        st.info("No hay datos para graficar")
        return
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df_agrupado = df.groupby(["Fecha", "Tipo"])["Monto"].sum().unstack().fillna(0)
    df_agrupado.plot(kind="line")
    st.pyplot(plt.gcf())

# Gráfico barras
def grafico_barras():
    df = cargar_datos()
    if df.empty:
        st.info("No hay datos para graficar")
        return
    resumen = df.groupby("Tipo")["Monto"].sum()
    resumen.plot(kind="bar", color=["green", "red"])
    st.pyplot(plt.gcf())

# Ejecución del menú
if menu == "📅 Registrar Ganancia":
    registrar("Ganancia")
elif menu == "📉 Registrar Gasto":
    registrar("Gasto")
elif menu == "📊 Resumen":
    mostrar_resumen()
elif menu == "📙 Historial":
    mostrar_historial()
elif menu == "📈 Gráfico Línea":
    grafico_linea()
elif menu == "📉 Gráfico Barras":
    grafico_barras()
