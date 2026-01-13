import customtkinter as ctk 
from PIL import Image, ImageTk
from utils.path import resource_path

amarelo = "#ffdf61"
roxo = "#402456"
rosa_escuro = "#b20f55"

def alerta_personalizado(titulo, msg):
    popup = ctk.CTkToplevel()
    popup.title(titulo)
    popup.geometry("300x150")
    label = ctk.CTkLabel(popup, text=msg, font=ctk.CTkFont(size=14))
    label.pack(pady=15)

    img_gato = Image.open(resource_path("assets/icone_gato.png"))
    img_gato = img_gato.resize((60, 60))
    img_gato_tk = ImageTk.PhotoImage(img_gato)

    label_img = ctk.CTkLabel(popup, image=img_gato_tk, text="")
    label_img.image = img_gato_tk
    label_img.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    botao_ok = ctk.CTkButton(popup, text="OK",corner_radius=10, fg_color=roxo, hover_color=rosa_escuro, command=popup.destroy)
    botao_ok.pack(pady=10)
    popup.grab_set() 