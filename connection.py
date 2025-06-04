import os
from dotenv import load_dotenv
import pyodbc

# Cargar variables de entorno
load_dotenv()

# Datos de conexión
server = os.getenv("DB_SERVER")    # Ejemplo: 'localhost' o '192.168.1.10'
database = os.getenv("DB_NAME") # Nombre de la base de datos
username = os.getenv("DB_USER")    # Usuario de SQL Server
password = os.getenv("DB_PASS")   # Contraseña del usuario

# Cadena de conexión
connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

try:
    # Establecer conexión
    conn = pyodbc.connect(connection_string)
    print("✅ Conexión exitosa a SQL Server")

except Exception as e:
    print("❌ Error al conectar a SQL Server:", e)
