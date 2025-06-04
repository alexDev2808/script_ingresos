# interfaz.py
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from querys import validar_puestos_en_db
from responsables import responsables
from main import construir_mapas_responsables, exportar_tabla_personal
import os
from datetime import datetime

def iniciar_interfaz():
    def seleccionar_archivo():
        filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not filepath or not os.path.isfile(filepath):
            messagebox.showwarning("Archivo no seleccionado", "Por favor selecciona un archivo válido.")
            return

        try:
            df_excel = pd.read_excel(filepath)
            if df_excel.empty:
                messagebox.showwarning("Archivo vacío", "El archivo Excel seleccionado no contiene datos.")
                return

            df_excel['NO EMP'] = df_excel['NO EMP'].astype(str).str.upper().str.strip()
            df_excel['id_empleado'] = '0' + df_excel['NO EMP']
            df_excel['id_area'] = df_excel['NO EMP'].apply(lambda x: 3 if x.endswith('L') else 6)
            df_excel['app'] = df_excel['APELLIDO PATERNO'].str.strip()
            df_excel['apm'] = df_excel['APELLIDO MATERNO'].str.strip()
            df_excel['nombre'] = df_excel['NOMBRE'].str.strip()
            df_excel['activo'] = 1
            df_excel['pass'] = df_excel['app'] + df_excel['id_empleado']

            puestos_unicos = df_excel['PUESTO'].dropna().str.strip().str.upper().unique()
            puestos_encontrados, puestos_no_encontrados = validar_puestos_en_db(puestos_unicos)

            if puestos_no_encontrados.empty is False:
                messagebox.showwarning("Puestos no encontrados", "Algunos puestos no se encontraron en la base de datos. Se guardarán en 'puestos_faltantes.csv'.")

            map_funciones = dict(zip(puestos_encontrados['PUESTO'], puestos_encontrados['id_funcion']))
            df_excel['PUESTO_NORMALIZADO'] = df_excel['PUESTO'].str.strip().str.upper()
            df_excel['id_funcion'] = df_excel['PUESTO_NORMALIZADO'].map(map_funciones)

            mapa_responsables, mapa_area_ids = construir_mapas_responsables(responsables)

            df_final = df_excel[[
                'id_empleado', 'id_funcion', 'id_area', 'app', 'apm', 'nombre', 'activo', 'pass'
            ]].copy()

            df_final['id_area_res'] = df_excel['PUESTO_NORMALIZADO'].map(mapa_responsables).fillna('')
            df_final['tc'] = 1
            df_final['mail'] = df_excel['E-MAIL'].str.strip()
            df_final['id_areat'] = df_excel['PUESTO_NORMALIZADO'].map(mapa_area_ids).fillna('')
            df_final['id_area_res2'] = 5
            df_final['id_area_res3'] = ''
            df_final['perm_fsm'] = 0
            df_final['tipoPuesto'] = 3

            df_final = df_final[[
                'id_empleado', 'id_funcion', 'id_area', 'app', 'apm', 'nombre', 'activo', 'pass',
                'id_area_res', 'tc', 'mail', 'id_areat', 'id_area_res2', 'id_area_res3', 'perm_fsm', 'tipoPuesto'
            ]]

            carpeta = "Ingresos"
            os.makedirs(carpeta, exist_ok=True)
            fecha_actual = datetime.now().strftime("%d_%m_%Y")
            nombre_base = f"PNIngreso_{fecha_actual}"
            ruta_archivo = os.path.join(carpeta, f"{nombre_base}.xlsx")
            contador = 1

            while os.path.exists(ruta_archivo):
                ruta_archivo = os.path.join(carpeta, f"{nombre_base}_{contador}.xlsx")
                contador += 1

            exportar_tabla_personal(df_final, ruta_archivo)
            puestos_no_encontrados.to_csv(os.path.join(carpeta, "puestos_faltantes.csv"), index=False)

            if os.path.isfile(ruta_archivo):
                messagebox.showinfo("Archivo importado", f"✅ El archivo ha sido importado correctamente en la carpeta 'Ingresos':\n{os.path.basename(ruta_archivo)}")
            else:
                messagebox.showwarning("Error", "No se encontró el archivo después del guardado.")

        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error al procesar el archivo:\n{str(e)}")

    root = tk.Tk()
    root.title("Generador de Tabla de Personal")
    root.geometry("400x200")

    boton = tk.Button(root, text="Seleccionar archivo Excel", command=seleccionar_archivo, height=2, width=30)
    boton.pack(pady=60)

    root.mainloop()

iniciar_interfaz()