import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mysql.connector

class VerDonante:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.tabla_donantes = None

        tk.Label(parent, text="Consulta de Donantes", font=("Arial", 16), bg="white").pack(pady=10)
        
        frame_busqueda = tk.Frame(parent, bg="white")
        frame_busqueda.pack(pady=10)

        tk.Label(frame_busqueda, text="Ingrese el DNI del donante:", bg="white").grid(row=0, column=0, padx=5)
        self.entrada_dni = tk.Entry(frame_busqueda, width=30)
        self.entrada_dni.grid(row=0, column=1, padx=5)

        tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            bg="#d4b3b3",
            command=self.realizar_busqueda
        ).grid(row=0, column=2, padx=5)

        columnas = ("ID", "Nombre", "Apellido", "Fecha Nacimiento", "Sexo", "DNI", "Teléfono", "Correo", "Dirección", "Última donación", "Tipo Sangre")
        self.tabla_donantes = ttk.Treeview(parent, columns=columnas, show="headings", height=15)

        for col in columnas:
            self.tabla_donantes.heading(col, text=col)
            self.tabla_donantes.column(col, width=100)

        self.tabla_donantes.pack(pady=20)

        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Editar Donante", bg="#a37676", fg="white", command=self.editar_donante).pack(side="left", padx=10)
        tk.Button(button_frame, text="Eliminar Donante", bg="#f8f8f8", command=self.eliminar_donante).pack(side="left", padx=10)
        tk.Button(self.parent, text="Cancelar", bg="#f8f8f8", command=self.limpiar).pack(side="top", padx=5)

    def realizar_busqueda(self):
        dni = self.entrada_dni.get()
        if not dni:
            messagebox.showwarning("Advertencia", "Por favor, ingrese un DNI válido.")
            return

        try:
            cursor = self.conn.cursor()
            query = """
                SELECT d.id, d.nombre, d.apellido, d.fecha_n, d.sexo, d.DNI, d.telefono, d.Correo, 
                       d.direccion, d.UltimaD, ts.TipodeSangre 
                FROM donante d 
                JOIN TipodeSangre ts ON ts.id = d.id_TipodeSangre 
                WHERE dni = %s
            """
            cursor.execute(query, (dni,))
            resultado = cursor.fetchall()

            for row in self.tabla_donantes.get_children():
                self.tabla_donantes.delete(row)

            if resultado:
                for registro in resultado:
                    self.tabla_donantes.insert("", "end", values=registro)
            else:
                messagebox.showinfo("Información", "No se encontró un donante con ese DNI.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al conectar con la base de datos: {e}")

    def editar_donante(self):
        seleccionado = self.tabla_donantes.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro para editar.")
            return

        valores = self.tabla_donantes.item(seleccionado)["values"]
        entrada_dni = valores[5]

        ventana_editar = tk.Toplevel()
        ventana_editar.title("Editar Donante")
        ventana_editar.geometry("800x800")

        etiquetas = ["Nombre", "Apellido", "Fecha Nacimiento", "Sexo", "DNI", "Teléfono","Correo", "Dirección","Última Donación", "Tipo Sangre"]
        entradas = []

        for i, campo in enumerate(valores[1:]):
            tk.Label(ventana_editar, text=etiquetas[i]).pack(pady=5)
            entrada = tk.Entry(ventana_editar)
            entrada.insert(0, campo)
            entrada.pack(pady=5)
            entradas.append(entrada)

        tk.Button(ventana_editar, text="Guardar Cambios", command=lambda: self.guardar_cambios(entrada_dni, entradas)).pack(pady=10)

    def guardar_cambios(self, entrada_dni, entradas):
        nuevos_datos = [entrada.get() for entrada in entradas]

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM TipodeSangre WHERE TipodeSangre = %s", (nuevos_datos[-1],))
            id_TipodeSangre = cursor.fetchone()
            if not id_TipodeSangre:
                messagebox.showerror("Error", "Tipo de Sangre no válido.")
                return
            id_TipodeSangre = id_TipodeSangre[0]

            update_query = """
            UPDATE donante
            SET nombre = %s, apellido = %s, fecha_n = %s, sexo = %s, DNI = %s,
                telefono = %s, Correo = %s, direccion = %s, UltimaD = %s, id_TipodeSangre = %s
            WHERE DNI = %s
            """
            cursor.execute(update_query, (*nuevos_datos[:-1], id_TipodeSangre, entrada_dni))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Datos actualizados correctamente.")
            self.realizar_busqueda()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar el donante: {e}")

    def eliminar_donante(self):
        seleccionado = self.tabla_donantes.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro para eliminar.")
            return

        valores = self.tabla_donantes.item(seleccionado)["values"]
        entrada_dni = valores[5]

        respuesta = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar este registro?")
        if respuesta:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                cursor.execute("DELETE FROM donante WHERE DNI = %s", (entrada_dni,))
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                self.conn.commit()
                messagebox.showinfo("Éxito", "Donante eliminado correctamente.")
                self.tabla_donantes.delete(seleccionado)
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"No se pudo eliminar el donante: {e}")

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
