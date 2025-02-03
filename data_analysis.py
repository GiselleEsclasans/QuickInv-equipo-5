# data_analysis.py

import pandas as pd

def cargar_datos(filepath: str) -> pd.DataFrame:
    """
    Carga un archivo CSV o Excel en un DataFrame de pandas.
    """
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
    return df

def calcular_estadisticas(df: pd.DataFrame) -> dict:
    """
    Devuelve algunas estadísticas descriptivas del DataFrame.
    """
    stats = {
        "filas": df.shape[0],
        "columnas": df.shape[1],
        "columnas_nombres": list(df.columns),
        "descripcion": df.describe(include='all').to_dict()
    }
    return stats
