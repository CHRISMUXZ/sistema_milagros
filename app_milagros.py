import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import calendar

# Configuración de página (esto siempre primero)
st.set_page_config(page_title="Sistema Financiero - Milagros", layout="centered")

# --- LOGIN SIMPLE ---
PASSWORD = "Milagritosgorditacerdita123"
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Acceso al Sistema Financiero de Milagros")
    password = st.text_input("Ingresa la contraseña:", type="password")

    if st.button("Ingresar"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.success("¡Bienvenido, Chris!")
            st.experimental_rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# --- CONFIGURACIÓN Y CARGA DE DATOS ---
file_path = "data_milagros.csv"
fecha_actual = datetime.now().strftime("%Y-%m-%d")
semana_actual = f"{datetime.now().isocalendar().year}-W{datetime.now().isocalendar().week}"

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame(columns=["Fecha", "Semana", "Tipo", "Descripción", "Monto"])

# --- FUNCIONES ---
def guardar_datos():
    df.to_csv(file_path, index=False)

def registrar_dato(tipo, descripcion, monto):
    global df
    nuevo = pd.DataFrame([{
        "Fecha": fecha_actual,
        "Semana": semana_actual,
        "Tipo": tipo,
        "Descripción": descripcion,
        "Monto": monto
    }])
    df = pd.concat([df, nuevo], ignore_index=True)
    guardar_datos()

def exportar_excel_automatico():
    nombre_archivo = f"milagros_semana_{semana_actual}.xlsx"
    df.to_excel(nombre_archivo, index=False)

# --- SIDEBAR MENÚ ---
with st.sidebar:
    st.title("📂 Menú de Opciones")
    menu = st.radio("", [
        "📅 Registrar Ganancia", "📉 Registrar Gasto", "📊 Resumen", 
        "📙 Historial", "📈 Gráfico Línea", "📉 Gráfico Barras"
    ])

# --- FUNCIONALIDADES ---
if menu == "📅 Registrar Ganancia":
    st.header("Registrar Ganancia")
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto (S/)", min_value=0.0, format="%.2f")
    if st.button("Registrar"):
        registrar_dato("Ganancia", descripcion, monto)
        st.success("✅ Ganancia registrada correctamente")

elif menu == "📉 Registrar Gasto":
    st.header("Registrar Gasto")
    descripcion = st.text_input("Descripción del Gasto")
    monto = st.number_input("Monto del Gasto (S/)", min_value=0.0, format="%.2f")
    if st.button("Registrar"):
        registrar_dato("Gasto", descripcion, monto)
        st.success("✅ Gasto registrado correctamente")

elif menu == "📊 Resumen":
    st.header("Resumen Financiero Semanal")
    df_semana = df[df["Semana"] == semana_actual]
    total_ganancia = df_semana[df_semana["Tipo"] == "Ganancia"]["Monto"].sum()
    total_gasto = df_semana[df_semana["Tipo"] == "Gasto"]["Monto"].sum()
    neto = total_ganancia - total_gasto

    st.metric("Ganancia Total", f"S/ {total_ganancia:.2f}")
    st.metric("Gasto Total", f"S/ {total_gasto:.2f}")
    st.metric("Ganancia Neta", f"S/ {neto:.2f}")

elif menu == "📙 Historial":
    st.header("Historial por Semana")
    semanas = df["Semana"].unique()
    semana_sel = st.selectbox("Selecciona una semana", sorted(semanas, reverse=True))
    df_sel = df[df["Semana"] == semana_sel]
    st.dataframe(df_sel)

elif menu == "📈 Gráfico Línea":
    st.header("Gráfico de Línea Semanal")
    resumen = df.groupby("Semana")["Monto"].sum().reset_index()
    plt.figure(figsize=(10, 5))
    plt.plot(resumen["Semana"], resumen["Monto"], marker='o', color='green')
    plt.xticks(rotation=45)
    plt.title("Evolución de Monto Total por Semana")
    st.pyplot(plt)

elif menu == "📉 Gráfico Barras":
    st.header("Gráfico de Barras: Ganancia vs Gasto")
    resumen = df.groupby(["Semana", "Tipo"])["Monto"].sum().unstack(fill_value=0).reset_index()
    resumen.plot(x="Semana", kind="bar", stacked=False, figsize=(10, 5))
    plt.xticks(rotation=45)
    plt.title("Ganancias y Gastos Semanales")
    st.pyplot(plt)

# --- EXPORTACIÓN AUTOMÁTICA ---
exportar_excel_automatico()
