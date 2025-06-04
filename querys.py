# querys.py
import pandas as pd
from connection import conn

def obtener_funciones():
    """Consulta todos los puestos registrados en la tabla Det_Funcion."""
    query = "SELECT id_funcion, funcion FROM Det_Funcion"
    df = pd.read_sql(query, conn)
    df['funcion'] = df['funcion'].str.strip().str.upper()
    conn.close()
    return df

def validar_puestos_en_db(puestos):
    """
    Compara una lista de puestos contra los existentes en Det_Funcion.
    Retorna dos DataFrames: encontrados y no encontrados.
    """
    df_funciones = obtener_funciones()
    df_puestos = pd.DataFrame({'PUESTO': [p.strip().upper() for p in puestos]})
    df_resultado = df_puestos.merge(df_funciones, how="left", left_on="PUESTO", right_on="funcion")
    encontrados = df_resultado.dropna(subset=["id_funcion"])[["PUESTO", "id_funcion"]]
    no_encontrados = df_resultado[df_resultado["id_funcion"].isna()][["PUESTO"]]
    return encontrados, no_encontrados
