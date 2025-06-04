# main.py
import pandas as pd
from querys import validar_puestos_en_db

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

# Construir tabla final con los campos solicitados
df_final = df_excel[[
    'id_empleado', 'id_funcion', 'id_area', 'app', 'apm', 'nombre', 'activo', 'pass'
]]

# Mostrar resultados finales
print("\n✅ Tabla final para inserción en la base de datos:")
print(df_final)

# Mostrar puestos no encontrados (opcional)
print("\n❌ Puestos no encontrados en la base de datos:")
print(puestos_no_encontrados)

# Guardar puestos no encontrados si se desea
puestos_no_encontrados.to_csv("puestos_faltantes.csv", index=False)