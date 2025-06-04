# main.py
import pandas as pd
from querys import validar_puestos_en_db
from responsables import responsables

def exportar_tabla_personal(df, nombre_archivo):
    """Exporta el DataFrame de personal a un archivo Excel."""
    df.to_excel(nombre_archivo, index=False)

# Construir mapas de puesto -> ID responsable y puesto -> AREA_ID
def construir_mapas_responsables(responsables):
    mapa_id_res = {}
    mapa_area_id = {}
    for item in responsables:
        for nombre, datos in item.items():
            for puesto in datos['PUESTOS']:
                key = puesto['NOMBRE'].strip().upper()
                mapa_id_res[key] = datos['ID']
                mapa_area_id[key] = puesto.get('AREA_ID', '')
    return mapa_id_res, mapa_area_id

# Ejecutar solo si se corre directamente
if __name__ == "__main__":
    # Cargar archivo Excel
    archivo_excel = "PersonalNuevoIngreso.xlsx"
    df_excel = pd.read_excel(archivo_excel)

    # Normalizar NO EMP y obtener id_empleado con 0 al inicio
    df_excel['NO EMP'] = df_excel['NO EMP'].astype(str).str.upper().str.strip()
    df_excel['id_empleado'] = '0' + df_excel['NO EMP']

    # Determinar id_area según sufijo 'L'
    df_excel['id_area'] = df_excel['NO EMP'].apply(lambda x: 3 if str(x).endswith('L') else 6)

    # Preparar campos base
    df_excel['app'] = df_excel['APELLIDO PATERNO'].str.strip()
    df_excel['apm'] = df_excel['APELLIDO MATERNO'].str.strip()
    df_excel['nombre'] = df_excel['NOMBRE'].str.strip()
    df_excel['activo'] = 1
    df_excel['pass'] = df_excel['app'] + df_excel['id_empleado']

    # Validar puestos contra la base de datos
    puestos_unicos = df_excel['PUESTO'].dropna().str.strip().str.upper().unique()
    puestos_encontrados, puestos_no_encontrados = validar_puestos_en_db(puestos_unicos)

    # Crear diccionario de puestos encontrados para mapear
    map_funciones = dict(zip(puestos_encontrados['PUESTO'], puestos_encontrados['id_funcion']))
    df_excel['PUESTO_NORMALIZADO'] = df_excel['PUESTO'].str.strip().str.upper()
    df_excel['id_funcion'] = df_excel['PUESTO_NORMALIZADO'].map(map_funciones)

    # Crear diccionarios de responsables por puesto
    mapa_responsables, mapa_area_ids = construir_mapas_responsables(responsables)

    # Construir tabla base
    df_final = df_excel[[
        'id_empleado', 'id_funcion', 'id_area', 'app', 'apm', 'nombre', 'activo', 'pass'
    ]].copy()

    # Agregar columnas adicionales
    df_final['id_area_res'] = df_excel['PUESTO_NORMALIZADO'].map(mapa_responsables).fillna('')
    df_final['tc'] = 1
    df_final['mail'] = df_excel['E-MAIL'].str.strip()
    df_final['id_areat'] = df_excel['PUESTO_NORMALIZADO'].map(mapa_area_ids).fillna('')
    df_final['id_area_res2'] = 5
    df_final['id_area_res3'] = ''
    df_final['perm_fsm'] = 0
    df_final['tipoPuesto'] = 3

    # Reorganizar columnas finales
    df_final = df_final[[
        'id_empleado', 'id_funcion', 'id_area', 'app', 'apm', 'nombre', 'activo', 'pass',
        'id_area_res', 'tc', 'mail', 'id_areat', 'id_area_res2', 'id_area_res3', 'perm_fsm', 'tipoPuesto'
    ]]

    # Mostrar resultados finales
    print("\n✅ Tabla final para inserción en la base de datos:")
    print(df_final)

    # Guardar tabla final en Excel
    exportar_tabla_personal(df_final, "tabla_personal_final.xlsx")

    # Mostrar puestos no encontrados (opcional)
    print("\n❌ Puestos no encontrados en la base de datos:")
    print(puestos_no_encontrados)

    # Guardar puestos no encontrados si se desea
    puestos_no_encontrados.to_csv("puestos_faltantes.csv", index=False)
