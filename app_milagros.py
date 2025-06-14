import streamlit as st
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="💸 Finanzas Milagros", layout="wide")
st.markdown("""
    <h1 style='text-align: center; color: #8e44ad;'>✨ Sistema Financiero - Tienda Milagros ✨</h1>
    <hr style='border: 1px solid #dcdcdc;'>
""", unsafe_allow_html=True)

# --- AUTENTICACIÓN ---
PASSWORD = "Milagritosgorditacerdita123"
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.title("🔐 Acceso restringido")
    password_input = st.text_input("Ingresa la contraseña:", type="password")
    if password_input == PASSWORD:
        st.session_state.autenticado = True
        st.rerun()
    elif password_input != "":
        st.error("❌ Contraseña incorrecta")
    st.stop()

# --- ARCHIVOS ---
ARCHIVO_HISTORIAL = "historial_semanal.json"
ARCHIVO_GANANCIAS = "ganancias.json"
ARCHIVO_GASTOS = "pagos.json"

def cargar_datos(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def guardar_datos(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

ganancias = cargar_datos(ARCHIVO_GANANCIAS)
gastos = cargar_datos(ARCHIVO_GASTOS)
historial = cargar_datos(ARCHIVO_HISTORIAL)

def verificar_cierre_semana():
    global ganancias, gastos, historial
    fechas_ganancias = {g["fecha"] for g in ganancias}
    fechas_gastos = {g["fecha"] for g in gastos}
    fechas_totales = sorted(fechas_ganancias.union(fechas_gastos))
    if len(fechas_totales) >= 7:
        semana_actual = fechas_totales[:7]
        total_ganado = sum(g["cantidad"] for g in ganancias if g["fecha"] in semana_actual)
        total_gastado = sum(g["cantidad"] for g in gastos if g["fecha"] in semana_actual)
        ganancia_neta = total_ganado - total_gastado

        historial.append({
            "semana": semana_actual,
            "ganado": total_ganado,
            "gastado": total_gastado,
            "neta": ganancia_neta
        })
        guardar_datos(ARCHIVO_HISTORIAL, historial)

        ganancias = [g for g in ganancias if g["fecha"] not in semana_actual]
        gastos = [g for g in gastos if g["fecha"] not in semana_actual]
        guardar_datos(ARCHIVO_GANANCIAS, ganancias)
        guardar_datos(ARCHIVO_GASTOS, gastos)

        # Exportación automática
        df = pd.DataFrame(historial)
        df.to_excel("historial_milagros.xlsx", index=False)

        st.success("✅ Semana cerrada y guardada en historial + Excel.")

def registrar_dato(tipo):
    st.markdown(f"## ➕ Registrar {tipo.capitalize()}")
    fecha = st.text_input("📅 Fecha (DD/MM)", value=datetime.now().strftime("%d/%m"), key=f"{tipo}_fecha")
    cantidad = st.number_input("💰 Monto", min_value=0.0, step=0.5, key=f"{tipo}_monto")
    descripcion = st.text_input("📝 Descripción", key=f"{tipo}_desc")
    if st.button(f"💾 Guardar {tipo.capitalize()}", key=f"{tipo}_boton"):
        entrada = {"fecha": fecha, "cantidad": cantidad, "descripcion": descripcion}
        if tipo == "ganancia":
            ganancias.append(entrada)
            guardar_datos(ARCHIVO_GANANCIAS, ganancias)
        else:
            gastos.append(entrada)
            guardar_datos(ARCHIVO_GASTOS, gastos)
        verificar_cierre_semana()
        st.success(f"✅ {tipo.capitalize()} registrada correctamente.")

def mostrar_resumen():
    st.markdown("## 📊 Resumen actual")
    total_ganado = sum(g["cantidad"] for g in ganancias)
    total_gastado = sum(g["cantidad"] for g in gastos)
    neta = total_ganado - total_gastado
    st.metric("Ganado", f"S/ {total_ganado:.2f}")
    st.metric("Gastado", f"S/ {total_gastado:.2f}")
    st.metric("Ganancia Neta", f"S/ {neta:.2f}")

def mostrar_historial():
    st.markdown("## 📚 Historial Semanal")
    for i, semana in enumerate(historial, 1):
        st.markdown(f"**Semana {i}**: {semana['semana'][0]} - {semana['semana'][-1]}")
        st.write(f"🔹 Ganado: S/ {semana['ganado']:.2f}")
        st.write(f"🔻 Gastado: S/ {semana['gastado']:.2f}")
        st.write(f"🟢 Neta: S/ {semana['neta']:.2f}")
        st.markdown("---")

def graficar():
    st.markdown("## 📈 Gráfico de Línea Semanal")
    if not historial:
        st.warning("⚠️ No hay datos para graficar.")
        return
    semanas = [f"Semana {i+1}" for i in range(len(historial))]
    ganados = [s['ganado'] for s in historial]
    gastados = [s['gastado'] for s in historial]
    netas = [s['neta'] for s in historial]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(semanas, ganados, marker='o', label='Ganado', color='green')
    ax.plot(semanas, gastados, marker='o', label='Gastado', color='red')
    ax.plot(semanas, netas, marker='o', label='Neta', color='blue')
    ax.set_title("Comparación Semanal")
    ax.set_ylabel("Monto (S/)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

def graficar_barras():
    st.markdown("## 📉 Gráfico de Barras")
    if not historial:
        st.warning("⚠️ No hay datos para graficar.")
        return
    semanas = [f"Semana {i+1}" for i in range(len(historial))]
    ganados = [s['ganado'] for s in historial]
    gastados = [s['gastado'] for s in historial]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(semanas, ganados, label='Ganado', color='seagreen')
    ax.bar(semanas, gastados, bottom=ganados, label='Gastado', color='salmon')
    ax.set_title("Ganancias vs Gastos")
    ax.set_ylabel("Montos (S/)")
    ax.legend()
    ax.grid(axis='y')
    st.pyplot(fig)

# --- SIDEBAR Y NAVEGACIÓN ---
with st.sidebar:
    st.image("logo_milagros.png", width=150)
    st.markdown("## 📂 Menú de Opciones")
    menu = st.radio("", [
        "📅 Registrar Ganancia", "📉 Registrar Gasto", "📊 Resumen", 
        "📙 Historial", "📈 Gráfico Línea", "📉 Gráfico Barras"
    ])


if menu == "📅 Registrar Ganancia":
    registrar_dato("ganancia")
elif menu == "📉 Registrar Gasto":
    registrar_dato("gasto")
elif menu == "📊 Resumen":
    mostrar_resumen()
elif menu == "📙 Historial":
    mostrar_historial()
elif menu == "📈 Gráfico Línea":
    graficar()
elif menu == "📉 Gráfico Barras":
    graficar_barras()
