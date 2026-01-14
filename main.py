import customtkinter as ctk
from interface.login import criar_tela_login
from utils.path import resource_path
import os

if __name__ == "__main__":
    try:
        import pyi_splash # type: ignore
        pyi_splash.close()
    except ImportError:
        pass

    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("Chat a Bit")
    app.geometry("500x600")

    caminho_cursor = resource_path("assets/cursor.cur").replace("\\", "/")
    app.configure(cursor=f"@{caminho_cursor}")

    criar_tela_login(app)

    app.mainloop()