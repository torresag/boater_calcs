import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import csv
from io import BytesIO, StringIO
from calculo_boater import calcular_costo, obtener_precios_lombardia

st.set_page_config(page_title="Boater - Calculadora de Costos", layout="centered")
st.title("⚓ Calculadora de Costos de Viaje - Boater")

tab1, tab2 = st.tabs(["🚤 Viaje individual", "📈 Comparar curvas de costo"])

# VIAJE INDIVIDUAL
with tab1:
    st.subheader("Viaje individual")

    tipo_motor = st.selectbox("Tipo de motor", [
        "motor fuera de borda",
        "motor interno nafta",
        "motor interno diesel"
    ])
    hp = st.number_input("HP (Caballos de fuerza)", min_value=10, max_value=300, step=10, value=100)
    velocidad = st.number_input("Velocidad crucero (nudos)", min_value=1, value=20, step=1, format="%d")
    asientos = st.number_input("Cantidad de asientos", min_value=1, max_value=30, value=6)
    distancia = st.number_input("Distancia del viaje (km)", min_value=1, value=10, step=1, format="%d")
    tiempo_espera = st.number_input("Tiempo de espera (horas)", min_value=0, value=0, step=1, format="%d")

    if st.button("Calcular costo individual"):
        try:
            precio_benzina, precio_gasolio = obtener_precios_lombardia()
            precio = precio_gasolio if "diesel" in tipo_motor else precio_benzina
            costo_km, costo_total = calcular_costo(tipo_motor, hp, velocidad, asientos, distancia, precio, tiempo_espera)

            st.success(f"Precio de combustible usado: €{precio:.3f}/litro")
            st.info(f"Costo por kilómetro: €{costo_km:.2f}")
            st.success(f"✅ Costo total estimado para {distancia:.1f} km: €{costo_total:.2f}")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# CURVAS DE COSTO
with tab2:
    st.subheader("Comparar curvas de costos")

    if "curvas" not in st.session_state:
        st.session_state.curvas = []

    with st.form("form_curva"):
        nombre = st.text_input("Nombre de la curva", value=f"Curva {len(st.session_state.curvas) + 1}")
        tipo_motor_c = st.selectbox("Tipo de motor", [
            "motor fuera de borda",
            "motor interno nafta",
            "motor interno diesel"
        ], key="motor_curva")
        hp_c = st.number_input("HP", min_value=10, max_value=300, value=100, step=10, format="%d", key="hp_curva")
        vel_c = st.number_input("Velocidad crucero (nudos)", min_value=1, max_value=100, value=20, step=1, format="%d", key="vel_curva")
        asientos_c = st.number_input("Asientos", min_value=1, max_value=30, value=6, step=1, format="%d", key="asientos_curva")
        espera_c = st.number_input("Tiempo de espera (horas)", min_value=0, max_value=24, value=0, step=1, format="%d", key="espera_curva")

        submitted = st.form_submit_button("Agregar curva")
        if submitted:
            precio_benzina, precio_gasolio = obtener_precios_lombardia()
            precio_c = precio_gasolio if "diesel" in tipo_motor_c else precio_benzina
            st.session_state.curvas.append({
                "nombre": nombre,
                "tipo_motor": tipo_motor_c,
                "hp": hp_c,
                "vel": vel_c,
                "asientos": asientos_c,
                "precio": precio_c,
                "espera": espera_c
            })
            st.success(f"Curva '{nombre}' agregada")

    if st.session_state.curvas:
        distancias = list(range(10, 101, 10))
        fig, ax = plt.subplots(figsize=(6, 4))
        csv_output = [["Curva", "Distancia (km)", "Costo (€)"]]

        for curva in st.session_state.curvas:
            costos = [calcular_costo(curva["tipo_motor"], curva["hp"], curva["vel"], curva["asientos"], d, curva["precio"], curva["espera"])[1] for d in distancias]
            ax.plot(distancias, costos, marker='o', label=curva["nombre"])
            for d, c in zip(distancias, costos):
                csv_output.append([curva["nombre"], d, f"{c:.2f}"])

        ax.set_title("Costo del viaje en función de la distancia")
        ax.set_xlabel("Distancia (km)")
        ax.set_ylabel("Costo (€)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # Gráfico de costo por asiento
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        csv_output_asiento = [["Curva", "Distancia (km)", "Costo por asiento (€)"]]
        for curva in st.session_state.curvas:
            costos_por_asiento = []
            for d in distancias:
                costo_total = calcular_costo(curva["tipo_motor"], curva["hp"], curva["vel"], curva["asientos"], d, curva["precio"], curva["espera"])[1]
                costo_asiento = costo_total / curva["asientos"]
                costos_por_asiento.append(costo_asiento)
                csv_output_asiento.append([curva["nombre"], d, f"{costo_asiento:.2f}"])
            ax2.plot(distancias, costos_por_asiento, marker='s', label=curva["nombre"])
        ax2.set_title("Costo por asiento en función de la distancia")
        ax2.set_xlabel("Distancia (km)")
        ax2.set_ylabel("Costo por asiento (€)")
        ax2.grid(True)
        ax2.legend()
        st.pyplot(fig2)

        # Exportar CSV con ambos conjuntos de datos
        csv_combined = StringIO()
        writer = csv.writer(csv_combined)
        writer.writerow(["Curva", "Distancia (km)", "Costo (€)", "", "Curva", "Distancia (km)", "Costo por asiento (€)"])
        for row1, row2 in zip(csv_output[1:], csv_output_asiento[1:]):
            writer.writerow(row1 + [""] + row2)
        csv_bytes = csv_combined.getvalue().encode("utf-8")
        st.download_button("📥 Descargar CSV", data=csv_bytes, file_name="curvas_costos.csv", mime="text/csv")

        # Exportar imagen combinada
        img_buffer = BytesIO()
        fig_all, (ax_all1, ax_all2) = plt.subplots(2, 1, figsize=(6, 8))
        for curva in st.session_state.curvas:
            costos = [calcular_costo(curva["tipo_motor"], curva["hp"], curva["vel"], curva["asientos"], d, curva["precio"], curva["espera"])[1] for d in distancias]
            ax_all1.plot(distancias, costos, marker='o', label=curva["nombre"])
            costos_asiento = [c / curva["asientos"] for c in costos]
            ax_all2.plot(distancias, costos_asiento, marker='s', label=curva["nombre"])
        ax_all1.set_title("Costo del viaje (€)")
        ax_all2.set_title("Costo por asiento (€)")
        for ax in (ax_all1, ax_all2):
            ax.set_xlabel("Distancia (km)")
            ax.set_ylabel("Costo (€)")
            ax.grid(True)
            ax.legend()
        fig_all.tight_layout()
        fig_all.savefig(img_buffer, format="png")
        st.download_button("🖼️ Descargar imagen", data=img_buffer.getvalue(), file_name="curvas_costos.png", mime="image/png")

        # Botón para limpiar
        if st.button("🗑️ Limpiar curvas"):
            st.session_state.curvas = []
