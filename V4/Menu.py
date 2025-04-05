import tkinter as tk
from PIL import Image, ImageTk
import mysql.connector
from RegistrarDonante import *
from VerDonante import *
from Reserva import *
from Verdonaciones import *
from SolicitudesTransfusion import *

class Menu:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Gestor Banco de Sangre")
        self.root.geometry("1200x800")
        self.root.configure(bg="#d9a5a5")


        self.conn = mysql.connector.connect(
            host="localhost",
            user="",
            password="",
            database="bancodesangre"
        )
        self.cursor = self.conn.cursor()


        sidebar = tk.Frame(root, bg="#d9a5a5", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

         # Definir fuente más grande
        btn_font = ("Arial", 50, "bold")  # Aumentar tamaño de la fuente

        buttons = [
            ("Registrar Donante", "👤", self.abrir_registro_donante),
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
                height=3,  # Aumentar altura del botón
                width=20,  # Aumentar ancho del botón
                command=command
            )
            button.pack(fill=tk.X, pady=5, padx=5)


        self.main_frame = tk.Frame(root, bg="white")
        self.main_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.content_frame = tk.Frame(self.main_frame, bg="white") #Es una especie de "pantalla" donde se cargan diferentes interfaces sin necesidad de abrir nuevas ventanas.
        self.content_frame.pack(expand= True, fill=tk.BOTH)

        self.agregar_logo()

    def abrir_registro_donante(self):
        self._limpiar_main_frame()
        RegistrarDonante(self.content_frame, self.conn)

    def abrir_consulta_donante(self):
        self._limpiar_main_frame()
        VerDonante(self.content_frame, self.conn)
    
    def abrir_stock(self):
        self._limpiar_main_frame()
        Reserva(self.content_frame, self.conn)

    def ver_donaciones(self):
        self._limpiar_main_frame()
        VerDonaciones(self.content_frame, self.conn)

    def abrir_solicitudes_transfusion(self):
        self._limpiar_main_frame()
        VerSolicitud(self.content_frame, self.conn)

    def agregar_logo(self):
        self._limpiar_main_frame()
        logo_path = "Banco.jpg"
        try:
            image = Image.open(logo_path)
            logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(self.content_frame, image=logo, bg="white")
            logo_label.image = logo
            logo_label.pack(pady=20)
        except Exception as e:
            tk.Label(self.content_frame, text="No se encontró el logo.", font=("Arial", 16), bg="white").pack()


    def _limpiar_main_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    


# La función main para iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = Menu(root)
    root.mainloop()
