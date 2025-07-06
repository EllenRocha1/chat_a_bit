import customtkinter as ctk
from interface.login import criar_tela_login
import os

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("Chat a Bit")
    app.geometry("500x600")

    caminho_cursor = os.path.abspath("assets/cursor.cur").replace("\\", "/")
    app.configure(cursor=f"@{caminho_cursor}")

    criar_tela_login(app)

    app.mainloop()