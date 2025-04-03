import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mysql.connector

class Reserva:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn

        tk.Label(parent, text="Reserva", font=("Arial", 16), bg="white").pack(pady=10)

        labels = ["Volúmen donado:", "Fecha de donación:", "Vencimiento:", "Tipo de Sangre:", "Estado:", "Id Donante:", "Id Compatibilidad:"]
        self.entries = {}

        # Frame contenedor horizontal
        horizontal_frame = tk.Frame(parent, bg="white")
        horizontal_frame.pack()

        for label in labels:
            frame = tk.Frame(horizontal_frame, bg="white")
            frame.pack(side="left", padx=10)  # Alinea los elementos en horizontal

            tk.Label(frame, text=label, font=("Arial", 12), bg="white").pack()
            entry = tk.Entry(frame)
            entry.pack()
            self.entries[label] = entry

        # Botones
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Guardar", bg="#a37676", fg="white", command=self.guardar_reserva).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancelar", bg="#f8f8f8", command=self.cancelar).pack(side="left", padx=10)

        self.cargar_stock()

        columnas = ("ID", "VolumenDisp", "Vencimiento", "TipoSangre")
        self.tabla_stock = ttk.Treeview(parent, columns=columnas, show="headings", height=15)

        for col in columnas:
            self.tabla_stock.heading(col, text=col)
            self.tabla_stock.column(col, width=120)

        self.tabla_stock.pack(pady=10)

        for stock in self.stock_data:
            self.tabla_stock.insert("", "end", values=stock)

        # Botones para editar y eliminar
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Editar Reserva", bg="#a37676", fg="white", command=self.editar_reserva).pack(side="left", padx=10)
        tk.Button(button_frame, text="Eliminar Reserva", bg="#f8f8f8", command=self.borrar_reserva).pack(side="left", padx=10)
        tk.Button(self.parent, text="Cancelar", bg="#f8f8f8", command=self.limpiar).pack(side="top", padx=5)

    def guardar_reserva(self):
        try:
            datos = {key: entry.get() for key, entry in self.entries.items()}
            if not all(datos.values()):
                raise ValueError("Todos los campos son obligatorios.")
            # Guardar en la base de datos
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO reserva (VolumenDisp, FechaExtraccion, Vencimiento, TipodeSangre, Estado, id_Donante, id_Compatibilidad)
                VALUES (%s, %s, %s, %s, %s, %s,  %s)
            ''', (datos["Volúmen donado:"], datos["Fecha de donación:"], datos["Vencimiento:"], datos["Tipo de Sangre:"], datos["Estado:"], datos["Id Donante:"], datos["Id Compatibilidad:"]))
            self.conn.commit()
            messagebox.showinfo("Éxito", "La donación ha sido registrada correctamente.")
            self.cargar_stock()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except mysql.connector.Error as err:
            messagebox.showerror("Error de base de datos", str(err))

    def cargar_stock(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT r.ID, r.VolumenDisp, r.Vencimiento, r.TipodeSangre
            FROM reserva r;
            ''')
            self.stock_data = cursor.fetchall()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo cargar el stock: {e}")
            self.stock_data = []

    def editar_reserva(self):
        seleccion = self.tabla_stock.selection()
        if seleccion:
            item = seleccion[0]
            valores = self.tabla_stock.item(item, "values")
            id_reserva = valores[0]
            volumen = valores[1]
            vencimiento = valores[2]
            tipo_sangre = valores[3]

            self.cancelar()

            tk.Label(self.parent, text="Editar Reserva", font=("Arial", 16), bg="white").pack(pady=10)

            tk.Label(self.parent, text="Volumen Disponible:", bg="white").pack()
            entrada_volumen = tk.Entry(self.parent)
            entrada_volumen.insert(0, volumen)
            entrada_volumen.pack()

            tk.Label(self.parent, text="Fecha de Vencimiento:", bg="white").pack()
            entrada_vencimiento = tk.Entry(self.parent)
            entrada_vencimiento.insert(0, vencimiento)
            entrada_vencimiento.pack()

            tk.Label(self.parent, text="Tipo de Sangre:", bg="white").pack()
            entrada_tipo_sangre = tk.Entry(self.parent)
            entrada_tipo_sangre.insert(0, tipo_sangre)
            entrada_tipo_sangre.pack()

            def guardar_cambios():
                nuevo_volumen = entrada_volumen.get()
                nuevo_vencimiento = entrada_vencimiento.get()
                nuevo_tipo_sangre = entrada_tipo_sangre.get()

                try:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        UPDATE reserva
                        SET VolumenDisp = %s, Vencimiento = %s, TipodeSangre = %s
                        WHERE ID = %s
                    ''', (nuevo_volumen, nuevo_vencimiento, nuevo_tipo_sangre, id_reserva))
                    self.conn.commit()
                    self.cargar_stock()
                    messagebox.showinfo("Éxito", "La reserva ha sido actualizada correctamente.")
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"No se pudo actualizar la reserva: {e}")

            tk.Button(self.parent, text='Guardar', bg='#a37676', fg='white', command=guardar_cambios).pack(pady=10)
            tk.Button(self.parent, text='Cancelar', bg='#ff6f61', fg='white', command=self.cargar_stock).pack(pady=10)
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna reserva para editar.")

    def borrar_reserva(self):
        seleccion = self.tabla_stock.selection()
        if seleccion:
            for item in seleccion:
                valores = self.tabla_stock.item(item, "values")
                id_reserva = valores[0]

                try:
                    cursor = self.conn.cursor()
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                    cursor.execute('DELETE FROM reserva WHERE ID = %s', (id_reserva,))
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                    self.conn.commit()
                    self.tabla_stock.delete(item)
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"No se pudo borrar la reserva: {e}")
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna reserva para editar.")

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
