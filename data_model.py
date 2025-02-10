# data_model.py
import pandas as pd

def cargar_datos(filepath: str):
    if not filepath:
        raise ValueError("La ruta del archivo es nula o vacía.")
    if filepath.endswith(".csv"):
        return pd.read_csv(filepath)
    elif filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        return pd.read_excel(filepath)
    else:
        raise ValueError("El archivo debe ser un CSV o un Excel.")

def calcular_estadisticas(df: pd.DataFrame) -> dict:
    return {
        "filas": df.shape[0],
        "columnas": df.shape[1],
        "columnas_nombres": list(df.columns),
    }