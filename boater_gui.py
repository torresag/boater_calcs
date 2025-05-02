import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv
from calculo_boater import calcular_costo, obtener_precios_lombardia
from io import BytesIO, StringIO

class BoaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Boater - Calculadora de Costos de Viaje")
        self.mostrar_inicio()

    def mostrar_inicio(self):
        self.limpiar()
        self.frame_inicio = ttk.Frame(self.root, padding=20)
        self.frame_inicio.pack()

        ttk.Label(self.frame_inicio, text="¿Qué deseas hacer?").pack(pady=10)
        ttk.Button(self.frame_inicio, text="Calcular viaje individual", command=self.viaje_individual).pack(fill='x', pady=5)
        ttk.Button(self.frame_inicio, text="Generar curva de costos", command=self.curva_costos).pack(fill='x', pady=5)

    def viaje_individual(self):
        self.limpiar()
        self.formulario_costo(tipo="individual")

    def curva_costos(self):
        self.limpiar()
        self.curvas_por_graficar = []
        self.curva_actual = 0

        frame = ttk.Frame(self.root, padding=20)
        frame.pack()

        # Always show form to add curves
        self.formulario_costo(tipo="curva")

    def limpiar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def formulario_costo(self, tipo):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack()

        entradas = {}

        campos = [
            ("Tipo de motor (motor fuera de borda / motor interno nafta / motor interno diesel)", "tipo_motor"),
            ("HP (caballos de fuerza)", "hp"),
            ("Velocidad crucero (nudos)", "vel_crucero"),
            ("Asientos", "asientos"),
        ]

        if tipo == "curva":
            campos.insert(0, ("Nombre (solo para curva)", "nombre"))

        if tipo == "individual":
            campos.append(("Distancia (km)", "distancia"))

        for label, key in campos:
            ttk.Label(frame, text=label).pack(anchor='w')
            if key == "tipo_motor":
                entradas[key] = ttk.Combobox(frame, values=[
                    "motor fuera de borda",
                    "motor interno nafta",
                    "motor interno diesel"
                ])
                entradas[key].set("motor fuera de borda")  # valor por defecto
            else:
                entradas[key] = ttk.Entry(frame)
            entradas[key].pack(fill='x', pady=2)

        def calcular():
            try:
                tipo_motor = entradas["tipo_motor"].get().strip().lower()
                hp = int(entradas["hp"].get())
                vel = float(entradas["vel_crucero"].get())
                asientos = int(entradas["asientos"].get())
                nombre = entradas.get("nombre", tk.StringVar()).get()

                precio_benzina, precio_gasolio = obtener_precios_lombardia()
                precio = precio_gasolio if tipo_motor == "motor interno diesel" else precio_benzina

                if tipo == "individual":
                    distancia = float(entradas["distancia"].get())
                    costo_km, total = calcular_costo(tipo_motor, hp, vel, asientos, distancia, precio)
                    messagebox.showinfo("Resultado",
                        f"Costo por km: €{costo_km:.2f}\nCosto total para {distancia} km: €{total:.2f}\nPrecio usado: €{precio:.3f}/litro")
                else:
                    self.curvas_por_graficar.append({
                        "nombre": nombre or f"Curva {len(self.curvas_por_graficar) + 1}",
                        "tipo_motor": tipo_motor,
                        "hp": hp,
                        "vel": vel,
                        "asientos": asientos,
                        "precio": precio
                    })
                    # After adding a curve, ask if user wants to add more or plot
                    if messagebox.askyesno("Agregar más curvas", "¿Deseas agregar otra curva?"):
                        self.limpiar()
                        self.formulario_costo(tipo="curva")
                    else:
                        self.graficar_curvas(self.curvas_por_graficar)
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(frame, text="Calcular", command=calcular).pack(pady=10)
        ttk.Button(frame, text="Volver al inicio", command=self.mostrar_inicio).pack()

    def graficar_curvas(self, curvas):
        distancias = list(range(10, 101, 10))

        self.limpiar()
        frame = ttk.Frame(self.root, padding=10)
        frame.pack()

        fig, ax = plt.subplots(figsize=(6, 4))

        for curva in curvas:
            costos = [calcular_costo(curva["tipo_motor"], curva["hp"], curva["vel"], curva["asientos"], d, curva["precio"])[1] for d in distancias]
            ax.plot(distancias, costos, marker='o', label=curva["nombre"])

        ax.set_title("Costo del viaje en función de la distancia")
        ax.set_xlabel("Distancia (km)")
        ax.set_ylabel("Costo (€)")
        ax.grid(True)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        ttk.Button(frame, text="Guardar imagen", command=lambda: fig.savefig('curva_costos.png')).pack(pady=5)

        def guardar_csv():
            csv_text = StringIO()
            writer = csv.writer(csv_text)
            writer.writerow(["Curva", "Distancia (km)", "Costo (€)"])
            for curva in curvas:
                for d in distancias:
                    costo = calcular_costo(
                        curva["tipo_motor"],
                        curva["hp"],
                        curva["vel"],
                        curva["asientos"],
                        d,
                        curva["precio"]
                    )[1]
                    writer.writerow([curva["nombre"], d, f"{costo:.2f}"])
            csv_bytes = csv_text.getvalue().encode("utf-8")
            with open("curvas_costos.csv", "wb") as f:
                f.write(csv_bytes)

        ttk.Button(frame, text="Guardar CSV", command=guardar_csv).pack(pady=5)

        ttk.Button(frame, text="Volver al inicio", command=self.mostrar_inicio).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = BoaterApp(root)
    root.mainloop()
