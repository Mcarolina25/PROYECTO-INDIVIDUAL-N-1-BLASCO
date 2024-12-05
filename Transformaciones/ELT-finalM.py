import pandas as pd
import numpy as np
import ast

# datasets
movies = pd.read_csv(r"C:\Users\Admin\Desktop\PROYECTO INDIVIDUAL 1º\Movies\movies_dataset.csv", low_memory=False)
credits = pd.read_csv(r"C:\Users\Admin\Desktop\PROYECTO INDIVIDUAL 1º\Movies\processed_credits_dataset.csv")

# Función para desanidar columnas
def desanidar_columna(df, columna, key):
    def obtener_valor(x):
        if pd.notnull(x) and x != 'nan':
            try:
                # convertir a un diccionario
                data = ast.literal_eval(x)
                if isinstance(data, dict):  # Verificar diccionario
                    return data.get(key)  # .get() para evitar KeyError
                else:
                    return None  # Retorna None si no es un diccionario
            except (ValueError, SyntaxError):
                return None  # Retorna None si hay un error en la conversión
        return None  # Retorna None si el valor es NaN o 'nan'

    df[columna] = df[columna].apply(obtener_valor)

# Desanidar columnas específicas
desanidar_columna(movies, 'belongs_to_collection', 'name')
desanidar_columna(movies, 'production_companies', 'name')
desanidar_columna(movies, 'production_countries', 'name')
desanidar_columna(movies, 'spoken_languages', 'name')

# Rellenar valores nulos:
movies['revenue'] = movies['revenue'].fillna(0)  # revenue se rellena con 0.
movies['budget'] = movies['budget'].fillna(0)  # budget se rellena con 0
movies = movies.dropna(subset=['release_date'])  # elimina las filas nulas.

# Formato de fechas:
# Convertir al formato AAAA-mm-dd
movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce') 
# Extraer el año en una nueva columna release_year.
movies['release_year'] = movies['release_date'].dt.year 

# Crear columna de retorno de inversión:
# Convertir a numérico
movies['budget'] = pd.to_numeric(movies['budget'], errors='coerce')

# Calcular el retorno
movies['return'] = movies.apply(lambda x: x['revenue'] / x['budget'] if x['budget'] > 0 else 0, axis=1)

# Eliminar columnas innecesarias:
movies = movies.drop(columns=['video', 'imdb_id', 'adult',
                               'original_title', 'poster_path', 'homepage'])

# Guardar dataset:
movies.to_csv(r"C:\Users\Admin\Desktop\PROYECTO INDIVIDUAL 1º\Movies\processed_movies_dataset.csv", index=False)

