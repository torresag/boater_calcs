
import matplotlib.pyplot as plt
from calculo_boater import calcular_costo, obtener_precios_lombardia

def main():
    curvas = []
    n = int(input("¿Cuántas curvas querés generar? "))

    # Obtener precios actualizados
    precio_benzina, precio_gasolio = obtener_precios_lombardia()

    for i in range(n):
        print(f"\n--- Curva {i+1} ---")
        nombre = input("Nombre de la curva: ")
        tipo_motor = input("Tipo de motor (motor fuera de borda / motor interno nafta / motor interno diesel): ").strip().lower()
        hp = int(input("Caballos de fuerza (HP): "))
        vel_crucero = float(input("Velocidad de crucero (nudos): "))
        asientos = int(input("Número de asientos: "))

        if tipo_motor == "motor interno diesel":
            precio_combustible = precio_gasolio
        else:
            precio_combustible = precio_benzina
        distancias = list(range(10, 101, 10))
        costos = []
        for d in distancias:
            _, costo_total = calcular_costo(tipo_motor, hp, vel_crucero, asientos, d, precio_combustible)
            costos.append(costo_total)

        curvas.append((nombre, distancias, costos))

    # Graficar
    for nombre, distancias, costos in curvas:
        plt.plot(distancias, costos, marker='o', label=nombre)

    plt.title("Costo del viaje en función de la distancia")
    plt.xlabel("Distancia (km)")
    plt.ylabel("Costo (€)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
