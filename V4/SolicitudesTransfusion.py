import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mysql.connector


class VerSolicitud:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.stock_data = []  # Inicializar lista de datos para evitar errores

        # Título
        tk.Label(self.parent, text="Solicitudes de Transfusión", font=("Arial", 16), bg="white").pack(pady=10)

        # Botón para agregar nueva solicitud
        tk.Button(self.parent, text="➕ Agregar Solicitud", bg="#4CAF50", fg="white", command=self.agregar_solicitud).pack(pady=5)

        # Cargar solicitudes
        self.cargar_solicitud()

        # Columnas para la tabla
        columnas = ("ID", "Hospital", "Dirección", "Teléfono", "Volumen Solicitado", "Estado", "Tipo de Sangre")
        self.tabla_solicitudes = ttk.Treeview(self.parent, columns=columnas, show="headings", height=15)

        for col in columnas:
            self.tabla_solicitudes.heading(col, text=col)
            self.tabla_solicitudes.column(col, width=120)

        self.tabla_solicitudes.pack(pady=10)

        # Insertar los datos de las solicitudes en la tabla
        self.mostrar_solicitudes()

        # Botones
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Editar Solicitud", bg="#a37676", fg="white", command=self.editar_solicitud).pack(side="left", padx=10)
        tk.Button(self.parent, text="Cancelar", bg="#f8f8f8", command=self.limpiar).pack(side="top", padx=5)

    def cargar_solicitud(self):
        """Carga las solicitudes desde la base de datos y las almacena en self.stock_data."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    SELECT h.id, h.Nombre, h.direccion, h.telefono, s.VolumenSolic, s.Estado, ts.TipodeSangre
                    FROM hospital h
                    JOIN solicitud s ON h.id = s.id_Hospital
                    JOIN tipodesangre ts ON ts.id = s.id_TipodeSangre;
                ''')
                self.stock_data = cursor.fetchall()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo cargar las solicitudes: {e}")
            self.stock_data = []

    def mostrar_solicitudes(self):
        """Muestra las solicitudes en la tabla."""
        for item in self.tabla_solicitudes.get_children():
            self.tabla_solicitudes.delete(item)

        for solicitud in self.stock_data:
            self.tabla_solicitudes.insert("", "end", values=solicitud)

    def agregar_solicitud(self):
        """Abre una ventana para agregar una nueva solicitud de transfusión."""
        ventana_nueva = tk.Toplevel(self.parent)
        ventana_nueva.title("Nueva Solicitud de Transfusión")
        ventana_nueva.geometry("400x400")

        labels = ["Hospital ID", "Volumen Solicitado", "Tipo de Sangre"]
        entradas = {}

        for label in labels:
            tk.Label(ventana_nueva, text=label).pack()
            entry = tk.Entry(ventana_nueva)
            entry.pack()
            entradas[label] = entry

        def guardar():
            id_hospital = entradas["Hospital ID"].get()
            volumen = entradas["Volumen Solicitado"].get()
            tipo_sangre = entradas["Tipo de Sangre"].get()

            if not (id_hospital and volumen and tipo_sangre):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            try:
                with self.conn.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO solicitud (id_Hospital, VolumenSolic, id_TipodeSangre)
                        VALUES (%s, %s, (SELECT id FROM tipodesangre WHERE TipodeSangre = %s))
                    ''', (id_hospital, volumen, tipo_sangre))
                    self.conn.commit()
                messagebox.showinfo("Éxito", "Solicitud agregada correctamente.")
                ventana_nueva.destroy()
                self.cargar_solicitud()
                self.mostrar_solicitudes()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"No se pudo agregar la solicitud: {e}")

        tk.Button(ventana_nueva, text="Guardar", bg="#4CAF50", fg="white", command=guardar).pack(pady=10)

    def editar_solicitud(self):
        """Permite editar una solicitud seleccionada de la tabla y, si es aceptada, descuenta la reserva."""
        seleccion = self.tabla_solicitudes.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud para editar.")
            return

        item = seleccion[0]
        valores = self.tabla_solicitudes.item(item, "values")
        id_solicitud = valores[0]  # ID de la solicitud
        volumen_solicitado = valores[4]  # Volumen solicitado
        tipo_sangre = valores[6]  # Tipo de sangre

        ventana_editar = tk.Toplevel(self.parent)
        ventana_editar.title("Editar Solicitud")
        ventana_editar.geometry("400x300")

        tk.Label(ventana_editar, text="Estado:").pack()
        entrada_estado = tk.Entry(ventana_editar)
        entrada_estado.insert(0, valores[5])  # Estado actual
        entrada_estado.pack()

        def guardar_cambios():
            nuevo_estado = entrada_estado.get().strip()

            try:
                with self.conn.cursor() as cursor:
                    # Actualizar el estado de la solicitud
                    cursor.execute('''
                        UPDATE solicitud SET Estado = %s WHERE ID = %s
                    ''', (nuevo_estado, id_solicitud))
                    self.conn.commit()

                    # Si el estado es "Aceptada", descontar del stock de sangre
                    if nuevo_estado.lower() == "aceptada":
                        cursor.execute('''
                            SELECT SUM(VolumenDisp) FROM reserva WHERE TipodeSangre = %s
                        ''', (tipo_sangre,))
                        volumen_disponible = cursor.fetchone()[0] or 0  # Si no hay stock, tomar 0

                        if float(volumen_disponible) == float(volumen_solicitado):
                            messagebox.showerror("Error", "No hay suficiente stock de sangre disponible.")
                            return
                        
                        
                        # Descontar sangre del stock
                        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                        cursor.execute('''
                        DELETE FROM reserva
                        WHERE TipodeSangre = %s AND VolumenDisp = %s
                        ORDER BY Vencimiento ASC LIMIT 1
                    ''', (tipo_sangre, volumen_solicitado))
                        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                        self.conn.commit()
                        messagebox.showinfo("Éxito", "Solicitud aceptada y stock actualizado correctamente.")

                ventana_editar.destroy()
                self.cargar_solicitud()
                self.mostrar_solicitudes()

            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"No se pudo actualizar la solicitud: {e}")

        tk.Button(ventana_editar, text="Guardar", command=guardar_cambios, bg="#a37676", fg="white").pack(pady=10)

    def borrar_solicitud(self):
        """Permite borrar una solicitud seleccionada de la tabla."""
        seleccion = self.tabla_solicitudes.selection()
        if seleccion:
            for item in seleccion:
                valores = self.tabla_solicitudes.item(item, "values")
                id_solicitud = valores[0]

                try:
                    with self.conn.cursor() as cursor:
                        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                        cursor.execute('DELETE FROM solicitud WHERE ID = %s', (id_solicitud,))
                        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                        self.conn.commit()
                    self.tabla_solicitudes.delete(item)
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"No se pudo borrar la solicitud: {e}")

    def limpiar(self):
        """Limpia la pantalla."""
        for widget in self.parent.winfo_children():
            widget.destroy()