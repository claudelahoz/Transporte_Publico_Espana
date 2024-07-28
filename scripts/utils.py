
""" Utils
Esta sección describe algunas de las utilidades adicionales disponibles dentro del módulo."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mysql.connector import Error
import mysql.connector
from datetime import datetime
import os

# Verificar valores atípicos

def identify_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
    return outliers


# Realiza la conexión con la base de datos
def create_connection():
    """Crea una conexión a la base de datos MySQL."""
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print('Conectado a la base de datos MySQL')
        return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

# Crea una tabla vacia en la base de datos
def create_table(cursor):
    """Crea la tabla si no existe."""
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS transporte_publico (
        id_viaje INT PRIMARY KEY,
        fecha DATETIME,
        ruta VARCHAR(100),
        numero_pasajeros INT,
        duracion_viaje_minutos INT,
        retraso_minutos INT,
        tipo_transporte VARCHAR(50),
        region VARCHAR(50),
        dia_semana VARCHAR(20)
    )
    '''
    try:
        cursor.execute(create_table_query)
        print("Tabla creada con éxito (si no existía)")
    except Error as e:
        print(f"Error al crear la tabla: {e}")

# Convierte las columnas a tipo time
def convert_date(date_str):
    """Convierte una cadena de fecha a objeto datetime."""
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# Insertar los datos en la tabla creada
def insert_data(cursor, data):
    """Inserta los datos en la tabla."""
    insert_query = '''
    INSERT INTO transporte_publico 
    (id_viaje, fecha, ruta, numero_pasajeros, duracion_viaje_minutos, 
     retraso_minutos, tipo_transporte, region, dia_semana)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    try:
        cursor.executemany(insert_query, data)
        print(f"{cursor.rowcount} filas insertadas.")
    except Error as e:
        print(f"Error al insertar datos: {e}")
        
# Función para visualizar la distribución
def plot_distribution(data, column, title):
    plt.figure(figsize=(10, 6))
    sns.histplot(data[column], kde=True)
    plt.title(title)
    plt.show()


# Función para Winsorización
def winsorize(s, limits):
    return s.clip(lower=s.quantile(limits[0]), upper=s.quantile(1 - limits[1]))

# Función para categorizar valores atípicos
def categorize_outliers(s, n_std=3):
    mean, std = s.mean(), s.std()
    cut_off = std * n_std
    lower, upper = mean - cut_off, mean + cut_off
    return pd.cut(s, bins=[-np.inf, lower, upper, np.inf], 
                  labels=['Extremo bajo', 'Normal', 'Extremo alto'])
