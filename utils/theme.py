import customtkinter as ctk

THEMES = {
    "dark": {
        "bg": "#1e1e1e",
        "bg_frame": "#2e2e2e",
        "text": "#FFFFFF",
        "primary": "#402456",
        "secondary": "#b20f55",
        "tertiary": "#ffdf61",
        "message_bg": "#3A3A3A",
        "user_list_bg": "#F6C6FA",
        "status_online": "#227522",
        "status_offline": "#B31B1B"
    },
    "light": {
        "bg": "#F5F2F7",
        "bg_frame": "#FFFFFF",
        "text": "#1A1124",
        "primary": "#532E70",
        "secondary": "#C81461",
        "tertiary": "#ffdf61",
        "message_bg": "#E0DCE3",
        "user_list_bg": "#F0E1F2",
        "status_online": "#227522",
        "status_offline": "#B31B1B"
    }
}

current_theme = "dark"
_callbacks = []

def get_colors():
    return THEMES.get(current_theme, THEMES["dark"])

def get_current_theme_name():
    return current_theme

def register_theme_callback(callback):
    if callback not in _callbacks:
        _callbacks.append(callback)

def unregister_theme_callback(callback):
    if callback in _callbacks:
        _callbacks.remove(callback)

def set_theme(theme_name):
    global current_theme
    if theme_name not in THEMES:
        theme_name = "dark"
    current_theme = theme_name
    
    ctk.set_appearance_mode("dark" if theme_name == "dark" else "light")
    
    for callback in _callbacks:
        try:
            callback()
        except Exception as e:
            print(f"Erro ao atualizar callback de tema: {e}")

def toggle_theme():
    novo_tema = "light" if current_theme == "dark" else "dark"
    set_theme(novo_tema)
