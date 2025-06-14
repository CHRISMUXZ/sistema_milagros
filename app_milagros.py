import streamlit as st
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ============================
# 🔐 AUTENTICACIÓN
# ============================
PASSWORD = "Milagritosgorditacerdita123"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acceso restringido")
    password_input = st.text_input("Ingresa la contraseña:", type="password")

    if password_input == PASSWORD:
        st.session_state.autenticado = True
        st.rerun()
    elif password_input != "":
        st.error("❌ Contraseña incorrecta")
    st.stop()

# ============================
# 📁 ARCHIVOS Y FUNCIONES BASE
# ============================
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

# ============================
# 📊 CARGA INICIAL DE DATOS
# ============================
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

        st.success("✅ Semana cerrada. Datos guardados en el historial.")

# ============================
# 💾 REGISTRAR GANANCIA / GASTO
# ============================
def registrar_dato(tipo):
    with st.expander(f"➕ Registrar {tipo.capitalize()}", expanded=True):
        fecha = st.text_input("📅 Fecha (DD/MM)", value=datetime.now().strftime("%d/%m"), key=f"{tipo}_fecha")
        cantidad = st.number_input("💰 Monto", min_value=0.0, step=0.5, key=f"{tipo}_monto")
        descripcion = st.text_input("📝 Descripción", key=f"{tipo}_descripcion")

        if st.button("Registrar", key=f"{tipo}_boton"):
            entrada = {"fecha": fecha, "cantidad": cantidad, "descripcion": descripcion}
            if tipo == "ganancia":
                ganancias.append(entrada)
                guardar_datos(ARCHIVO_GANANCIAS, ganancias)
            else:
                gastos.append(entrada)
                guardar_datos(ARCHIVO_GASTOS, gastos)
            verificar_cierre_semana()
            st.success(f"✅ {tipo.capitalize()} registrada correctamente.")

# ============================
# 📌 RESUMEN ACTUAL
# ============================
def mostrar_resumen():
    with st.expander("📊 Resumen actual", expanded=True):
        total_ganado = sum(g["cantidad"] for g in ganancias)
        total_gastado = sum(g["cantidad"] for g in gastos)
        neta = total_ganado - total_gastado
        st.metric("💵 Ganado", f"S/ {total_ganado:.2f}")
        st.metric("💸 Gastado", f"S/ {total_gastado:.2f}")
        st.metric("📈 Ganancia Neta", f"S/ {neta:.2f}")

# ============================
# 📚 HISTORIAL SEMANAL
# ============================
def mostrar_historial():
    with st.expander("📅 Historial Semanal", expanded=False):
        for i, semana in enumerate(historial, 1):
            st.markdown(f"**Semana {i}**: {semana['semana'][0]} - {semana['semana'][-1]}")
            st.write(f"- 🟢 Ganado: S/ {semana['ganado']:.2f}")
            st.write(f"- 🔴 Gastado: S/ {semana['gastado']:.2f}")
            st.write(f"- ⚖️ Neta: S/ {semana['neta']:.2f}")

# ============================
# 📈 GRÁFICA DE GANANCIA NETA
# ============================
def graficar():
    with st.expander("📈 Gráfica de Ganancia Neta por Semana", expanded=False):
        if not historial:
            st.warning("⚠️ No hay datos suficientes para graficar.")
            return
        semanas = list(range(1, len(historial)+1))
        netas = [s['neta'] for s in historial]
        fig, ax = plt.subplots()
        ax.plot(semanas, netas, marker='o', color='green')
        ax.set_title("📊 Ganancia Neta por Semana - Tienda Milagros")
        ax.set_xlabel("Semana")
        ax.set_ylabel("Ganancia Neta (S/)")
        ax.grid(True)
        st.pyplot(fig)

# ============================
# 🎛️ INTERFAZ PRINCIPAL
# ============================
st.title("💼 Finanzas - Tienda Milagros")
menu = st.sidebar.selectbox("Menú", ["Registrar Ganancia", "Registrar Gasto", "Resumen", "Historial", "Gráfica"])

if menu == "Registrar Ganancia":
    registrar_dato("ganancia")
elif menu == "Registrar Gasto":
    registrar_dato("gasto")
elif menu == "Resumen":
    mostrar_resumen()
elif menu == "Historial":
    mostrar_historial()
elif menu == "Gráfica":
    graficar()
