import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mysql.connector

# Definición de la función buscarDonaciones
def buscarDonaciones(cnx, id_donante):
    try:
        cursor = cnx.cursor()
        consulta = "SELECT id_Donante, Fecha, volumenDonado, Estado FROM Donacion WHERE id_Donante = %s"
        cursor.execute(consulta, (id_donante,))
        resultados = cursor.fetchall()
        return resultados
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error al buscar las donaciones: {e}")
        return None

# Clase Donante
class Donante:
    @staticmethod
    def buscar_donante(cnx, dni):
        try:
            cursor = cnx.cursor()
            cursor.execute(f"SELECT d.id, d.nombre, d.apellido, d.fecha_n, d.sexo, d.DNI, d.telefono, d.Correo, d.direccion, d.UltimaD, ts.TipodeSangre FROM donante d JOIN TipodeSangre ts ON ts.id = d.id_TipodeSangre WHERE dni = '{dni}'")
            resultado = cursor.fetchall()
            return resultado
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al buscar el DNI: {e}")
            return None

# Clase RegistroDonanteApp
class RegistroDonanteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Gestor Banco de Sangre")
        self.root.geometry("1200x800")
        self.root.configure(bg="#d9a5a5")

        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bancodesangre"
        )
        self.cursor = self.conn.cursor()

        sidebar = tk.Frame(root, bg="#d9a5a5", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        buttons = [
            ("Registrar Donante", "👤", self.abrir_registro_donante),
            ("Registrar Donación", "💧", self.abrir_registro_donacion),
            ("Ver Donantes", "👀", self.abrir_consulta_donante),
            ("Ver Reserva", "📦", self.abrir_stock),
            ("Ver Donaciones", "🔍", self.ver_donaciones),
            ("Solicitudes de Transfusión", "🩸", self.abrir_solicitudes_transfusion),
        ]

        for text, icon, command in buttons:
            button = tk.Button(
                sidebar,
                text=f"{icon} {text}",
                bg="#f2e2e2",
                fg="#333",
                anchor="w",
                padx=10,
                relief="flat",
                command=command
            )
            button.pack(fill=tk.X, pady=5, padx=5)

        self.main_frame = tk.Frame(root, bg="white")
        self.main_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.agregar_logo()

    def _limpiar_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def cargar_tipos_sangre(self):
        try:
            self.cursor.execute("SELECT TipodeSangre FROM tipodesangre")
            tipos_sangre = [row[0] for row in self.cursor.fetchall()]
            return tipos_sangre
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar los tipos de sangre: {e}")
            return []

    def abrir_consulta_donante(self):
        self._limpiar_main_frame()
        tk.Label(self.main_frame, text="Consulta de Donantes", font=("Arial", 16), bg="white").pack(pady=10)
        
        frame_busqueda = tk.Frame(self.main_frame, bg="white")
        frame_busqueda.pack(pady=10)

        tk.Label(frame_busqueda, text="Ingrese el DNI del donante:", bg="white").grid(row=0, column=0, padx=5)
        entrada_dni = tk.Entry(frame_busqueda, width=30)
        entrada_dni.grid(row=0, column=1, padx=5)

        tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            bg="#d4b3b3",
            command=lambda: self.realizar_busqueda(entrada_dni, tabla_donantes)
        ).grid(row=0, column=2, padx=5)

        columnas = ("ID", "Nombre", "Apellido", "Fecha Nacimiento", "Sexo", "DNI", "Teléfono", "Correo", "Dirección", "Última donación", "Tipo Sangre")
        tabla_donantes = ttk.Treeview(self.main_frame, columns=columnas, show="headings", height=15)

        for col in columnas:
            tabla_donantes.heading(col, text=col)
            tabla_donantes.column(col, width=100)

        tabla_donantes.pack(pady=20)

        boton_editar = tk.Button(self.main_frame, text="Editar Donante", command=lambda: self.editar_donante(tabla_donantes))
        boton_editar.pack(side="left", padx=20)

        boton_eliminar = tk.Button(self.main_frame, text="Eliminar Donante", command=lambda: self.eliminar_donante(tabla_donantes))
        boton_eliminar.pack(side="right", padx=20)

    def realizar_busqueda(self, entrada_dni, tabla_donantes):
        dni = entrada_dni.get()
        if not dni:
            messagebox.showwarning("Advertencia", "Por favor, ingrese un DNI válido.")
            return

        try:
            registros = Donante.buscar_donante(self.conn, dni)

            for row in tabla_donantes.get_children():
                tabla_donantes.delete(row)

            if registros:
                for registro in registros:
                    tabla_donantes.insert("", "end", values=registro)
            else:
                messagebox.showinfo("Información", "No se encontró un donante con ese DNI.")

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al conectar con la base de datos: {e}")

    def editar_donante(self, tabla_donantes):
        seleccionado = tabla_donantes.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro para editar.")
            return

        valores = tabla_donantes.item(seleccionado)["values"]
        id_donante = valores[0]

        ventana_editar = tk.Toplevel()
        ventana_editar.title("Editar Donante")
        ventana_editar.geometry("800x600")

        etiquetas = ["Nombre", "Apellido", "DNI", "Fecha Nacimiento", "Edad", "Género", "Dirección", "Tipo Sangre"]
        entradas = []

        for i, campo in enumerate(valores[1:]):
            etiqueta = tk.Label(ventana_editar, text=etiquetas[i])
            etiqueta.pack(pady=5)
            entrada = tk.Entry(ventana_editar)
            entrada.insert(0, campo)
            entrada.pack(pady=5)
            entradas.append(entrada)

        tk.Button(ventana_editar, text="Guardar Cambios", command=lambda: self.guardar_cambios(id_donante, entradas, ventana_editar)).pack(pady=10)

    def guardar_cambios(self, id_donante, entradas, ventana_editar):
        nuevos_datos = [entrada.get() for entrada in entradas]
        try:
            cursor = self.conn.cursor()
            update_query = """
            UPDATE donante 
            SET nombre = %s, apellido = %s, dni = %s, fecha_nacimiento = %s,
                edad = %s, genero = %s, direccion = %s, tipo_sangre = %s
            WHERE id = %s
            """
            cursor.execute(update_query, (*nuevos_datos, id_donante))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Datos actualizados correctamente.")
            self.realizar_busqueda(entradas[-1], self.main_frame)  # Actualizar la tabla
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar el donante: {e}")
        finally:
            ventana_editar.destroy()

    def eliminar_donante(self, tabla_donantes):
        seleccionado = tabla_donantes.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un registro para eliminar.")
            return

        valores = tabla_donantes.item(seleccionado)["values"]
        id_donante = valores[0]

        respuesta = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar este registro?")
        if respuesta:
            try:
                cursor = self.conn.cursor()
                delete_query = f"DELETE FROM donante WHERE id = {id_donante}"
                cursor.execute(delete_query)
                self.conn.commit()
                messagebox.showinfo("Éxito", "Donante eliminado correctamente.")
                self.realizar_busqueda(tabla_donantes.selection(), tabla_donantes)
            except mysql.connector.Error as e:
                                messagebox.showerror("Error", f"No se pudo eliminar el donante: {e}")

    def abrir_registro_donante(self):
        self._limpiar_main_frame()
        tk.Label(self.main_frame, text="Registrar Donante", font=("Arial", 16), bg="white").pack(pady=10)

        labels = ["Nombre:", "Apellido:", "Fecha de Nacimiento:", "Sexo:", "DNI:", "Celular:", "Correo:", "Direccion:", "Ultima Donacion:"]
        self.entries = {}
        for label in labels:
            frame = tk.Frame(self.main_frame, bg="white")
            frame.pack(pady=5)
            tk.Label(frame, text=label, font=("Arial", 12), bg="white").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="left")
            self.entries[label] = entry

        # ComboBox para seleccionar el tipo de sangre
       
        tipo_sangre_frame = tk.Frame(self.main_frame, bg="white")
        tipo_sangre_frame.pack(pady=10)
        tk.Label(tipo_sangre_frame, text="Tipo de Sangre:", font=("Arial", 12), bg="white").pack(side="left")
        tipos_sangre = self.cargar_tipos_sangre()
        self.tipo_sangre_cb = ttk.Combobox(tipo_sangre_frame, values=tipos_sangre)
        self.tipo_sangre_cb.pack(side="left", padx=5)
        tipo_sangre_frame.pack(pady=10, anchor="center")

        button_frame = tk.Frame(self.main_frame, bg="white")
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Guardar", bg="#a37676", fg="white", command=self.guardar_donante).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancelar", bg="#f8f8f8", command=self.agregar_logo).pack(side="left", padx=10)

    def guardar_donante(self):
        try:
            datos = {key: entry.get() for key, entry in self.entries.items()}
            datos["Tipo de Sangre:"] = self.tipo_sangre_cb.get()
            if not all(datos.values()):
                raise ValueError("Todos los campos son obligatorios.")
            # Guardar en la base de datos
            self.cursor.execute('''
                INSERT INTO donante (nombre, apellido, fecha_n, sexo, dni, telefono, correo, direccion, ultimaD, id_TipodeSangre)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, (
                    SELECT id FROM tipodesangre WHERE TipodeSangre = %s
                ))
            ''', (datos["Nombre:"], datos["Apellido:"], datos["Fecha de Nacimiento:"], datos["Sexo:"], datos["DNI:"], datos["Celular:"], datos["Correo:"], datos["Direccion:"], datos["Ultima Donacion:"], datos["Tipo de Sangre:"]))
            self.conn.commit()
            messagebox.showinfo("Exito", f"Donante {datos['Nombre:']} registrado correctamente.")
            self.agregar_logo()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except mysql.connector.Error as err:
            messagebox.showerror("Error de base de datos", str(err))

    def abrir_registro_donacion(self):
        self._limpiar_main_frame()
        tk.Label(self.main_frame, text="Registrar Donación", font=("Arial", 16), bg="white").pack(pady=10)
        labels = ["ID del Donante:", "Fecha de donación:", "Volúmen donado:", "Estado:"]
        self.entries = {}
        for label in labels:
            frame = tk.Frame(self.main_frame, bg="white")
            frame.pack(pady=5)
            tk.Label(frame, text=label, font=("Arial", 12), bg="white").pack(side="left")
            entry = tk.Entry(frame)
            entry.pack(side="left")
            self.entries[label] = entry
        button_frame = tk.Frame(self.main_frame, bg="white")
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Guardar", bg="#a37676", fg="white", command=self.guardar_donacion).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancelar", bg="#f8f8f8", command=self.agregar_logo).pack(side="left", padx=10)

    def guardar_donacion(self):
        try:
            datos = {key: entry.get() for key, entry in self.entries.items()}
            if not all(datos.values()):
                raise ValueError("Todos los campos son obligatorios.")
            # Guardar en la base de datos
            self.cursor.execute('''
                INSERT INTO donacion (id_Donante, Fecha, volumenDonado, Estado)
                VALUES (%s, %s, %s, %s)
            ''', (datos["ID del Donante:"], datos["Fecha de donación:"], datos["Volúmen donado:"], datos["Estado:"]))
            self.conn.commit()
            messagebox.showinfo("Exito", f"La donación ha sido registrada correctamente.")
            self.agregar_logo()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except mysql.connector.Error as err:
            messagebox.showerror("Error de base de datos", str(err))

    def abrir_stock(self):
        self._limpiar_main_frame()
        tk.Label(self.main_frame, text="Reserva", font=("Arial", 16), bg="white").pack(pady=10)

        self.cargar_stock()

        columnas = ("ID", "VolumenDisp", "Vencimiento", "TipoSangre")
        self.tabla_stock = ttk.Treeview(self.main_frame, columns=columnas, show="headings", height=15)

        for col in columnas:
            self.tabla_stock.heading(col, text=col)
            self.tabla_stock.column(col, width=120)
    
        self.tabla_stock.pack(pady=10)

        for stock in self.stock_data:
            self.tabla_stock.insert("", "end", values=stock)

        boton_Editar = tk.Button(self.main_frame, text='Editar reserva', bg='#a37676', fg='white', command=self.editar_reserva)
        boton_Editar.place(x=350, y=400)

        boton_Baja = tk.Button(self.main_frame, text='Borrar Reserva', bg='#ff6f61', fg='white', command=self.borrar_reserva)
        boton_Baja.place(x=450, y=400)

    def cargar_stock(self):
        try:
            self.cursor.execute('''
            SELECT r.ID, r.VolumenDisp, r.Vencimiento, ts.TipodeSangre
            FROM reserva r
            JOIN donante d ON r.id_donante = d.id
            JOIN tipodesangre ts ON d.id_TipodeSangre = ts.id
            ''')
            self.stock_data = self.cursor.fetchall()
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

            self._limpiar_main_frame()
            tk.Label(self.main_frame, text="Editar Reserva", font=("Arial", 16), bg="white").pack(pady=10)

            tk.Label(self.main_frame, text="Volumen Disponible:", bg="white").pack()
            entrada_volumen = tk.Entry(self.main_frame)
            entrada_volumen.insert(0, volumen)
            entrada_volumen.pack()

            tk.Label(self.main_frame, text="Fecha de Vencimiento:", bg="white").pack()
            entrada_vencimiento = tk.Entry(self.main_frame)
            entrada_vencimiento.insert(0, vencimiento)
            entrada_vencimiento.pack()

            tk.Label(self.main_frame, text="Tipo de Sangre:", bg="white").pack()
            entrada_tipo_sangre = tk.Entry(self.main_frame)
            entrada_tipo_sangre.insert(0, tipo_sangre)
            entrada_tipo_sangre.pack()

            def guardar_cambios():
                nuevo_volumen = entrada_volumen.get()
                nuevo_vencimiento = entrada_vencimiento.get()
                nuevo_tipo_sangre = entrada_tipo_sangre.get()

                try:
                    self.cursor.execute('''
                        UPDATE reserva
                        SET VolumenDisp = %s, Vencimiento = %s, TipodeSangre = %s
                        WHERE ID = %s
                    ''', (nuevo_volumen, nuevo_vencimiento, nuevo_tipo_sangre, id_reserva))
                    self.conn.commit()
                    self.abrir_stock()
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"No se pudo actualizar la reserva: {e}")

            tk.Button(self.main_frame, text='Guardar', bg='#a37676', fg='white', command=guardar_cambios).pack(pady=10)
            tk.Button(self.main_frame, text='Cancelar', bg='#ff6f61', fg='white', command=self.abrir_stock).pack(pady=10)
        else:
                        messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna reserva para editar.")

    def borrar_reserva(self):
        seleccion = self.tabla_stock.selection()
        if seleccion:
            for item in seleccion:
                valores = self.tabla_stock.item(item, "values")
                id_reserva = valores[0]

                try:
                    self.cursor.execute('DELETE FROM reserva WHERE ID = %s', (id_reserva,))
                    self.conn.commit()
                    self.tabla_stock.delete(item)
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"No se pudo borrar la reserva: {e}")
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna reserva para borrar.")

    def agregar_logo(self):
        self._limpiar_main_frame()
        logo_path = "Banco.jpg"
        try:
            image = Image.open(logo_path)
            logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(self.main_frame, image=logo, bg="white")
            logo_label.image = logo
            logo_label.pack(pady=20)
        except Exception as e:
            tk.Label(self.main_frame, text="No se encontró el logo.", font=("Arial", 16), bg="white").pack()

    def abrir_solicitudes_transfusion(self):
        self._limpiar_main_frame()
        tk.Label(self.main_frame, text="Solicitudes de Transfusión", font=("Arial", 16), bg="white").pack(pady=10)

        self.cargar_solicitud()

        columnas = ("ID", "Hospital", "Direccion", "Telefono", "Volumen Solicitado", "Tipo de Sangre")
        self.tabla_solicitudes = ttk.Treeview(self.main_frame, columns=columnas, show="headings", height=15)

        for col in columnas:
            self.tabla_solicitudes.heading(col, text=col)
            self.tabla_solicitudes.column(col, width=120)
    
        self.tabla_solicitudes.pack(pady=10)

        for solicitud in self.stock_data:
            self.tabla_solicitudes.insert("", "end", values=solicitud)

        boton_Editar = tk.Button(self.main_frame, text='Editar Solicitud', bg='#a37676', fg='white', command=self.editar_solicitud)
        boton_Editar.place(x=350, y=400)

        boton_Baja = tk.Button(self.main_frame, text='Borrar Solicitud', bg='#ff6f61', fg='white', command=self.borrar_solicitud)
        boton_Baja.place(x=450, y=400)

    def cargar_solicitud(self):
        try:
            self.cursor.execute('''
            SELECT h.id, h.Nombre, h.direccion, h.telefono, s.VolumenSolic, ts.TipodeSangre 
            FROM hospital h
            JOIN solicitud s ON h.id = s.id_Hospital
            JOIN tipodesangre ts ON ts.id = s.id_TipodeSangre;
            ''')
            self.stock_data = self.cursor.fetchall()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo cargar las solicitudes: {e}")
            self.stock_data = []

    def editar_solicitud(self):
        seleccion = self.tabla_solicitudes.selection()
        if seleccion:
            item = seleccion[0]
            valores = self.tabla_solicitudes.item(item, "values")
            id_solicitud = valores[0]
            volumen = valores[4]
            tipo_sangre = valores[5]

            self._limpiar_main_frame()
            tk.Label(self.main_frame, text="Editar Solicitud", font=("Arial", 16), bg="white").pack(pady=10)

            tk.Label(self.main_frame, text="Volumen Solicitado:", bg="white").pack()
            entrada_volumen = tk.Entry(self.main_frame)
            entrada_volumen.insert(0, volumen)
            entrada_volumen.pack()

            tk.Label(self.main_frame, text="Tipo de Sangre:", bg="white").pack()
            entrada_tipo_sangre = tk.Entry(self.main_frame)
            entrada_tipo_sangre.insert(0, tipo_sangre)
            entrada_tipo_sangre.pack()

            def guardar_cambios():
                nuevo_volumen = entrada_volumen.get()
                nuevo_tipo_sangre = entrada_tipo_sangre.get()
                print(f"Debug: nuevo_volumen={nuevo_volumen}, nuevo_tipo_sangre={nuevo_tipo_sangre}")  # Línea de depuración

                if not nuevo_tipo_sangre:
                    messagebox.showerror("Error", "El campo 'Tipo de Sangre' no puede estar vacío.")
                    return

                try:
                    self.cursor.execute('''
                        UPDATE solicitud
                        SET VolumenSolic = %s, id_TipodeSangre = (
                            SELECT id FROM tipodesangre WHERE TipodeSangre = %s
                        )
                        WHERE ID = %s
                    ''', (nuevo_volumen, nuevo_tipo_sangre, id_solicitud))
                    self.conn.commit()
                    self.abrir_solicitudes_transfusion()
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"No se pudo actualizar la solicitud: {e}")

            tk.Button(self.main_frame, text='Guardar', bg='#a37676', fg='white', command=guardar_cambios).pack(pady=10)
            tk.Button(self.main_frame, text='Cancelar', bg='#ff6f61', fg='white', command=self.abrir_solicitudes_transfusion).pack(pady=10)
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna solicitud para editar.")

    def borrar_solicitud(self):
        seleccion = self.tabla_solicitudes.selection()
        if seleccion:
            for item in seleccion:
                valores = self.tabla_solicitudes.item(item, "values")
                id_solicitud = valores[0]

                try:
                    self.cursor.execute('DELETE FROM solicitud WHERE ID = %s', (id_solicitud,))
                    self.conn.commit()
                    self.tabla_solicitudes.delete(item)
                except mysql.connector.Error as e:
                    messagebox.showerror("Error", f"No se pudo borrar la solicitud: {e}")
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna solicitud para borrar.")

    def ver_donaciones(self):
        self._limpiar_main_frame()
        VerDonacionesApp(self.main_frame, self.conn)

class VerDonacionesApp:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn

        tk.Label(self.root, text="Ver Donaciones", font=("Arial", 16), bg="#f8f8f8").pack(pady=10)

        frame_busqueda = tk.Frame(self.root, bg="#f8f8f8")
        frame_busqueda.pack(pady=10)

        tk.Label(frame_busqueda, text="ID Donante:", bg="#f8f8f8").grid(row=0, column=0, padx=5)
        self.entry_id_donante = tk.Entry(frame_busqueda, width=30)
        self.entry_id_donante.grid(row=0, column=1, padx=5)

        tk.Button(
            frame_busqueda,
            text="🔍 Buscar",
            bg="#d4b3b3",
            command=self.buscar_donaciones
        ).grid(row=0, column=2, padx=5)

        self.tree = ttk.Treeview(self.root, columns=("ID Donante", "Fecha", "Volumen", "Estado"), show="headings", height=8)
        self.tree.pack(pady=10)

        self.tree.heading("ID Donante", text="ID Donante")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Volumen", text="Volumen Donado")
        self.tree.heading("Estado", text="Estado")

        self.tree.column("ID Donante", width=100, anchor="center")
        self.tree.column("Fecha", width=150, anchor="center")
        self.tree.column("Volumen", width=100, anchor="center")
        self.tree.column("Estado", width=100, anchor="center")

        frame_botones = tk.Frame(self.root, bg="#f8f8f8")
        frame_botones.pack(pady=10)

        tk.Button(
            frame_botones,
            text="Editar Información",
            bg="#b3d4b3",
            command=self.editar_donacion
        ).grid(row=0, column=0, padx=10)

        tk.Button(self.root, text="Salir", bg="#d4b3b3", command=self.root.quit).pack(pady=10)

    def buscar_donaciones(self):
        id_donante = self.entry_id_donante.get()
        if not id_donante.isdigit():
            messagebox.showerror("Error", "El ID del Donante debe contener solo números.")
            return

        try:
            resultados = buscarDonaciones(self.conn, id_donante)
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

        ventana_editar = tk.Toplevel(self.root)
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
                cursor.execute('''
                    UPDATE Donacion
                    SET Fecha = %s, VolumenDonado = %s, Estado = %s
                    WHERE id_Donante = %s AND Fecha = %s
                ''', (nueva_fecha, nuevo_volumen, nuevo_estado, datos[0], datos[1]))
                self.conn.commit()
                cursor.close()

                messagebox.showinfo("Éxito", "Donación actualizada correctamente.")
                ventana_editar.destroy()
                self.buscar_donaciones()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"No se pudo actualizar la donación: {e}")

        tk.Button(ventana_editar, text="Guardar", command=guardar_cambios, bg="#a37676", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

# La función main para iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroDonanteApp(root)
    root.mainloop()
