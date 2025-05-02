import pandas as pd
import requests
import pdfplumber
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Nueva versión de la función obtener_precios_lombardia con valores por defecto en caso de error
def obtener_precios_lombardia():
    url = "https://www.mimit.gov.it/images/stories/carburanti/MediaRegionaleStradale.pdf"
    pdf_path = "MediaRegionaleStradale.pdf"
    response = requests.get(url)
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split("\n")
                for i, line in enumerate(lines):
                    if "Lombardia" in line:
                        try:
                            gasolio_line = lines[i + 2]  # gasolio está dos líneas después
                            benzina_line = lines[i + 3]  # benzina está tres líneas después
                            precio_gasolio = float(gasolio_line.split()[-1].replace(',', '.'))
                            precio_benzina = float(benzina_line.split()[-1].replace(',', '.'))
                            return precio_benzina, precio_gasolio
                        except (IndexError, ValueError):
                            continue
    except Exception:
        pass

    # Si no se encuentra o hay error, devolver valores por defecto
    print("⚠️  No se pudieron obtener los precios actuales. Usando valores por defecto.")
    return 1.84, 1.75


# Función para obtener el valor más cercano
def obtener_valor_mas_cercano(col_list, valor):
    return min(col_list, key=lambda x: abs(float(x) - valor))

def calcular_costo(tipo_motor, hp, vel_crucero, asientos, distancia, precio_combustible):
    # Cargar las tablas desde Excel
    df = pd.read_excel("Boater_excel.xlsx", sheet_name="Foglio1")

    # Procesar tabla HP
    tabla_hp = df.set_index("Caballos de fuerza").iloc[0:3]
    tabla_hp.index = tabla_hp.index.str.lower()

    # Procesar tabla asientos
    tabla_asientos = df.iloc[4:].dropna(how="all", axis=1).reset_index(drop=True)

    # Constantes por tipo de motor
    coeficientes = {
        "motor fuera de borda": 0.46,
        "motor interno nafta": 0.30,
        "motor interno diesel": 0.25,
    }

    if tipo_motor not in coeficientes:
        raise ValueError("Tipo de motor no reconocido.")

    # Obtener columna más cercana en tabla HP
    columnas_hp = [col for col in tabla_hp.columns if not pd.isnull(col)]
    col_hp_cercano = obtener_valor_mas_cercano(columnas_hp, hp)
    factor_hp = tabla_hp.loc[tipo_motor, col_hp_cercano]

    # Procesar tabla de asientos
    tabla_asientos.columns = tabla_asientos.iloc[1]
    tabla_asientos = tabla_asientos.drop(index=[0,1]).reset_index(drop=True)
    tabla_asientos["Asientos"] = tabla_asientos["Asientos"].str.lower()
    columnas_asientos = [col for col in tabla_asientos.columns if not pd.isnull(col) and col != "Asientos"]
    col_asientos_cercano = obtener_valor_mas_cercano(columnas_asientos, asientos)
    fila_asientos = tabla_asientos[tabla_asientos["Asientos"] == tipo_motor]
    factor_asientos = fila_asientos[col_asientos_cercano].values[0]

    # Cálculo
    consumo = (hp * coeficientes[tipo_motor]) / (vel_crucero * 1.852)
    costo_por_km = consumo * 3 * precio_combustible * factor_hp * factor_asientos
    costo_total = costo_por_km * distancia

    return costo_por_km, costo_total

def calcular_costo_viaje():
    # Entradas del usuario
    tipo_motor = input("Tipo de motor (Motor fuera de borda / Motor interno nafta / Motor interno diesel): ").strip().lower()
    hp = int(input("Caballos de fuerza (HP): "))
    vel_crucero = float(input("Velocidad de crucero (nudos): "))
    precio_benzina, precio_gasolio = obtener_precios_lombardia()
    if tipo_motor == "motor interno diesel":
        precio_combustible = precio_gasolio
    else:
        precio_combustible = precio_benzina
    asientos = int(input("Número de asientos: "))
    distancia = float(input("Distancia a recorrer (km): "))

    costo_por_km, costo_total = calcular_costo(tipo_motor, hp, vel_crucero, asientos, distancia, precio_combustible)

    # Resultado
    print(f"\nCosto por kilómetro: €{costo_por_km:.2f}")
    print(f"Costo total estimado para {distancia} km: €{costo_total:.2f}")
    print(f"Precio utilizado: €{precio_combustible:.3f}/litro")
    print(f"(Fuente: precios oficiales MIMIT para Lombardía)")

if __name__ == "__main__":
    calcular_costo_viaje()