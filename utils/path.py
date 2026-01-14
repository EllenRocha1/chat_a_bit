import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        # Mude de resource_path(".") para os.path.abspath(".")
        base_path = os.path.abspath(".") 
    return os.path.join(base_path, relative_path)

