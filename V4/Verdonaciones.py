import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mysql.connector


class VerDonaciones:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn

        tk.Label(parent, text="Ver Donaciones", font=("Arial", 16), bg="white").pack(pady=10)

        frame_busqueda = tk.Frame(parent, bg="white")
        frame_busqueda.pack(pady=10)

        tk.Label(frame_busqueda, text="ID Donante:", bg="white").grid(row=0, column=0, padx=5)
        self.entry_id_donante = tk.Entry(frame_busqueda, width=30)
        self.entry_id_donante.grid(row=0, column=1, padx=5)

        tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            bg="#d4b3b3",
            command=self.buscar_donaciones
        ).grid(row=0, column=2, padx=5)

        self.tree = ttk.Treeview(parent, columns=("ID Donante", "FechaExtraccion", "VolumenDisp", "Estado"), show="headings", height=8)
        self.tree.pack(pady=10)

        self.tree.heading("ID Donante", text="ID Donante")
        self.tree.heading("FechaExtraccion", text="Fecha")
        self.tree.heading("VolumenDisp", text="Volumen Donado")
        self.tree.heading("Estado", text="Estado")

        self.tree.column("ID Donante", width=100, anchor="center")
        self.tree.column("FechaExtraccion", width=150, anchor="center")
        self.tree.column("VolumenDisp", width=100, anchor="center")
        self.tree.column("Estado", width=100, anchor="center")

        frame_botones = tk.Frame(parent, bg="#f8f8f8")
        frame_botones.pack(pady=10)

        tk.Button(
            frame_botones,
            text="Editar Información",
            bg="#a37676",
            fg="white",
            command=self.editar_donacion
        ).grid(row=0, column=0, padx=10)

        tk.Button(self.parent, text="Cancelar", bg="#f8f8f8", command=self.limpiar).pack(side="top", padx=5)

    def buscar_donaciones(self):
        id_donante = self.entry_id_donante.get()
        if not id_donante.isdigit():
            messagebox.showerror("Error", "El ID del Donante debe contener solo números.")
            return

        try:
            cursor = self.conn.cursor()
            consulta = "SELECT id_Donante, FechaExtraccion, VolumenDisp, Estado FROM reserva WHERE id_Donante = %s"
            cursor.execute(consulta, (id_donante,))
            resultados = cursor.fetchall()
            cursor.close()

            if resultados:
                self.mostrar_resultados(resultados)
            else:
                messagebox.showinfo("Información", "No se encontraron donaciones para este ID Donante.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")

    def mostrar_resultados(self, datos):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for fila in datos:
            self.tree.insert("", "end", values=fila)

    def editar_donacion(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Debe seleccionar un registro para editar.")
            return

        item = self.tree.item(selected_item[0])
        datos = item["values"]

        ventana_editar = tk.Toplevel(self.parent)
        ventana_editar.title("Editar Donación")
        ventana_editar.geometry("400x300")

        tk.Label(ventana_editar, text="Fecha:").grid(row=0, column=0, padx=10, pady=5)
        fecha_entry = tk.Entry(ventana_editar)
        fecha_entry.insert(0, datos[1])
        fecha_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(ventana_editar, text="Volumen Donado:").grid(row=1, column=0, padx=10, pady=5)
        volumen_entry = tk.Entry(ventana_editar)
        volumen_entry.insert(0, datos[2])
        volumen_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(ventana_editar, text="Estado:").grid(row=2, column=0, padx=10, pady=5)
        estado_entry = tk.Entry(ventana_editar)
        estado_entry.insert(0, datos[3])
        estado_entry.grid(row=2, column=1, padx=10, pady=5)

        def guardar_cambios():
            nueva_fecha = fecha_entry.get()
            nuevo_volumen = volumen_entry.get()
            nuevo_estado = estado_entry.get()

            try:
                cursor = self.conn.cursor()
                update_query = '''
                    UPDATE reserva
                    SET FechaExtraccion = %s, VolumenDisp = %s, Estado = %s
                    WHERE id_Donante = %s AND FechaExtraccion = %s
                '''
                cursor.execute(update_query, (nueva_fecha, nuevo_volumen, nuevo_estado, datos[0], datos[1]))
                self.conn.commit()
                cursor.close()

                messagebox.showinfo("Éxito", "Donación actualizada correctamente.")
                ventana_editar.destroy()
                self.buscar_donaciones()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"No se pudo actualizar la donación: {e}")

        tk.Button(ventana_editar, text="Guardar", command=guardar_cambios, bg="#a37676", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

    def cancelar(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def limpiar(self):
        self.cancelar()
        logo_path = "imagenbanco.jpg"
        try:
            image = Image.open(logo_path)
            logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(self.parent, image=logo, bg="white")
            logo_label.image = logo
            logo_label.pack(pady=20)
        except Exception as e:
            tk.Label(self.parent, text="No se encontró el logo.", font=("Arial", 16), bg="white").pack()
