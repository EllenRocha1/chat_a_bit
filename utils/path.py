import sys
import os

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funciona no dev e no PyInstaller """
    try:
        # O PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = resource_path(".")
    return os.path.join(base_path, relative_path)