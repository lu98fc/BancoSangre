import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mysql.connector

class RegistrarDonante:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn

        tk.Label(parent, text="Registrar Donante", font=("Arial", 16), bg="white").pack(pady=10)

        labels = ["Nombre:", "Apellido:", "Fecha de Nacimiento:", "Sexo:", "DNI:", "Celular:", "Correo:", "Direccion:", "Ultima Donacion:"]
        self.entries = {}
        for label in labels:
            frame = tk.Frame(parent, bg="white")
            frame.pack(pady=5)
            tk.Label(frame, text=label, font=("Arial", 12), bg="white").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="left")
            self.entries[label] = entry

        # ComboBox para seleccionar el tipo de sangre
        tipo_sangre_frame = tk.Frame(parent, bg="white")
        tipo_sangre_frame.pack(pady=10)
        tk.Label(tipo_sangre_frame, text="Tipo de Sangre:", font=("Arial", 12), bg="white").pack(side="left")
        tipos_sangre = self.cargar_tipos_sangre()
        self.tipo_sangre_cb = ttk.Combobox(tipo_sangre_frame, values=tipos_sangre)
        self.tipo_sangre_cb.pack(side="left", padx=5)
        tipo_sangre_frame.pack(pady=10, anchor="center")

        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Guardar", bg="#a37676", fg="white", command=self.guardar_donante).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancelar", bg="#f8f8f8", command=self.limpiar).pack(side="left", padx=10)

    def cargar_tipos_sangre(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT TipodeSangre FROM tipodesangre")
            return [row[0] for row in cursor.fetchall()]
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al cargar tipos de sangre: {e}")
            return []

    def guardar_donante(self):
        try:
            cursor = self.conn.cursor()
            datos = {key: entry.get() for key, entry in self.entries.items()}
            datos["Tipo de Sangre:"] = self.tipo_sangre_cb.get()
            if not all(datos.values()):
                raise ValueError("Todos los campos son obligatorios.")
            cursor.execute('''
                INSERT INTO donante (nombre, apellido, fecha_n, sexo, dni, telefono, correo, direccion, ultimaD, id_TipodeSangre)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, (
                    SELECT id FROM tipodesangre WHERE TipodeSangre = %s
                ))
            ''', (datos["Nombre:"], datos["Apellido:"], datos["Fecha de Nacimiento:"], datos["Sexo:"], datos["DNI:"], datos["Celular:"], datos["Correo:"], datos["Direccion:"], datos["Ultima Donacion:"], datos["Tipo de Sangre:"]))
            self.conn.commit()
            cursor.close()
            messagebox.showinfo("Exito", f"Donante {datos['Nombre:']} registrado correctamente.")
            self.limpiar()  # Volver al inicio completamente después de registrar
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except mysql.connector.Error as err:
            messagebox.showerror("Error de base de datos", str(err))

    def cancelar(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def limpiar(self):
        self.cancelar()
        logo_path = "Banco.jpg"
        try:
            image = Image.open(logo_path)
            logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(self.parent, image=logo, bg="white")
            logo_label.image = logo
            logo_label.pack(pady=20)
        except Exception as e:
            tk.Label(self.parent, text="No se encontró el logo.", font=("Arial", 16), bg="white").pack()

    def agregar_logo(self):
        logo_path = "Banco.jpg"
        try:
            image = Image.open(logo_path)
            logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(self.parent, image=logo, bg="white")
            logo_label.image = logo
            logo_label.pack(pady=20)
        except Exception as e:
            tk.Label(self.parent, text="No se encontró el logo.", font=("Arial", 16), bg="white").pack()

