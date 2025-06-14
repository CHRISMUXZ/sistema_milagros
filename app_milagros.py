import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt
# Al inicio del script
import streamlit as st

# Login simple
def login():
    st.title("🔒 Acceso al Sistema Financiero")
    password = st.text_input("Contraseña", type="password")
    if password == "Milagritosgorditacerdita123":
        st.success("Acceso concedido")
        return True
    elif password:
        st.error("Contraseña incorrecta")
        return False
    return False

# Validar acceso antes de cargar el resto de la app
if not login():
    st.stop()



# Configuración inicial
st.set_page_config(page_title="Sistema Financiero - Milagros", layout="centered")

st.title("✨ Sistema Financiero - Tienda Milagros ✨")

# Nombre del archivo de base de datos
archivo_excel = "registro_milagros.xlsx"

# Cargar datos si existe el archivo
if os.path.exists(archivo_excel):
    df = pd.read_excel(archivo_excel)
else:
    df = pd.DataFrame(columns=["Fecha", "Tipo", "Monto", "Descripción"])

# Guardado automático cada 7 días
ultima_fecha = df["Fecha"].max() if not df.empty else None
hoy = datetime.datetime.today().date()

if ultima_fecha is None or (hoy - pd.to_datetime(ultima_fecha).date()).days >= 7:
    df.to_excel(archivo_excel, index=False)

# Funciones principales
def registrar_dato(tipo):
    global df  # <- Esto debe ir aquí arriba
    st.subheader(f"Registrar {tipo}")
    monto = st.number_input("Monto (S/.)", min_value=0.0, step=0.1, format="%.2f")
    descripcion = st.text_input("Descripción")
    fecha = st.date_input("Fecha", value=datetime.date.today())

    if st.button("Guardar"):
        if monto > 0 and descripcion.strip() != "":
            nuevo = pd.DataFrame([[fecha, tipo, monto, descripcion]], columns=df.columns)
            df = pd.concat([df, nuevo], ignore_index=True)
            df.to_excel(archivo_excel, index=False)
            st.success(f"{tipo} registrada correctamente.")
        else:
            st.error("Por favor, completa todos los campos.")

def mostrar_historial():
    st.subheader("📙 Historial Completo")
    st.dataframe(df)

    if st.button("📤 Exportar a Excel"):
        df.to_excel("registro_exportado.xlsx", index=False)
        st.success("Datos exportados correctamente como 'registro_exportado.xlsx'.")

def resumen_semanal():
    st.subheader("📊 Resumen Semanal")
    hoy = datetime.datetime.today().date()
    semana_actual = hoy - datetime.timedelta(days=7)
    df_reciente = df[pd.to_datetime(df["Fecha"]).dt.date >= semana_actual]

    ingresos = df_reciente[df_reciente["Tipo"] == "Ganancia"]["Monto"].sum()
    egresos = df_reciente[df_reciente["Tipo"] == "Gasto"]["Monto"].sum()
    neto = ingresos - egresos

    st.write(f"🟢 Ganancias (últimos 7 días): S/ {ingresos:.2f}")
    st.write(f"🔴 Gastos (últimos 7 días): S/ {egresos:.2f}")
    st.write(f"🟡 Ganancia Neta: S/ {neto:.2f}")

def grafico_linea():
    st.subheader("📈 Gráfico de Línea")
    if df.empty:
        st.warning("No hay datos para mostrar.")
        return

    df_ordenado = df.copy()
    df_ordenado["Fecha"] = pd.to_datetime(df_ordenado["Fecha"])
    df_ordenado = df_ordenado.sort_values("Fecha")

    ganancias = df_ordenado[df_ordenado["Tipo"] == "Ganancia"]
    gastos = df_ordenado[df_ordenado["Tipo"] == "Gasto"]

    plt.figure(figsize=(10, 5))
    plt.plot(ganancias["Fecha"], ganancias["Monto"], label="Ganancia", marker="o", color="green")
    plt.plot(gastos["Fecha"], gastos["Monto"], label="Gasto", marker="x", color="red")
    plt.xlabel("Fecha")
    plt.ylabel("Monto (S/.)")
    plt.title("Historial Financiero")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

def grafico_barras():
    st.subheader("📉 Gráfico de Barras por Semana")
    if df.empty:
        st.warning("No hay datos para mostrar.")
        return

    df_temp = df.copy()
    df_temp["Fecha"] = pd.to_datetime(df_temp["Fecha"])
    df_temp["Semana"] = df_temp["Fecha"].dt.strftime('%Y-%U')

    resumen = df_temp.groupby(["Semana", "Tipo"])["Monto"].sum().unstack(fill_value=0)
    resumen["Ganancia Neta"] = resumen.get("Ganancia", 0) - resumen.get("Gasto", 0)

    resumen[["Ganancia", "Gasto", "Ganancia Neta"]].plot(kind="bar", figsize=(10, 6), stacked=False)
    plt.title("Resumen Semanal")
    plt.ylabel("Monto (S/.)")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Menú lateral
with st.sidebar:
    st.markdown("## 📂 Menú de Opciones")
    menu = st.radio("Selecciona una opción", [
        "📅 Registrar Ganancia",
        "📉 Registrar Gasto",
        "📊 Resumen",
        "📙 Historial",
        "📈 Gráfico Línea",
        "📉 Gráfico Barras"
    ])

# Opciones del menú
if menu == "📅 Registrar Ganancia":
    registrar_dato("Ganancia")
elif menu == "📉 Registrar Gasto":
    registrar_dato("Gasto")
elif menu == "📊 Resumen":
    resumen_semanal()
elif menu == "📙 Historial":
    mostrar_historial()
elif menu == "📈 Gráfico Línea":
    grafico_linea()
elif menu == "📉 Gráfico Barras":
    grafico_barras()
