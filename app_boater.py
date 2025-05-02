
import streamlit as st
from calculo_boater import calcular_costo, obtener_precios_lombardia

st.set_page_config(page_title="Boater - Calculadora de Costos", layout="centered")
st.title("⚓ Calculadora de Costos de Viaje - Boater")

st.markdown("Calcula el costo estimado de un viaje en barco en función de los parámetros técnicos.")

tipo_motor = st.selectbox("Tipo de motor", [
    "motor fuera de borda",
    "motor interno nafta",
    "motor interno diesel"
])

hp = st.number_input("HP (Caballos de fuerza)", min_value=10, max_value=300, step=10, value=100)
velocidad = st.number_input("Velocidad crucero (nudos)", min_value=1.0, value=20.0)
asientos = st.number_input("Cantidad de asientos", min_value=1, max_value=30, value=6)
distancia = st.number_input("Distancia del viaje (km)", min_value=1.0, value=10.0)

if st.button("Calcular costo"):
    try:
        precio_benzina, precio_gasolio = obtener_precios_lombardia()
        precio = precio_gasolio if "diesel" in tipo_motor else precio_benzina

        costo_km, costo_total = calcular_costo(tipo_motor, hp, velocidad, asientos, distancia, precio)

        st.success(f"Precio de combustible usado: €{precio:.3f}/litro")
        st.info(f"Costo por kilómetro: €{costo_km:.2f}")
        st.success(f"✅ Costo total estimado para {distancia:.1f} km: €{costo_total:.2f}")
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
