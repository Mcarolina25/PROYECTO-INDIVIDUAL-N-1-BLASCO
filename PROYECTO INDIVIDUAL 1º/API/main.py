from fastapi import FastAPI
import pandas as pd

# Crear la estructura básica
app = FastAPI()

# Cargar el dataset procesado
movies = pd.read_csv('C:/Users/Admin/Desktop/PROYECTO INDIVIDUAL 1º/Movies/processed_movies_dataset.csv', low_memory=False)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de películas"}

# Filmaciones por mes
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    mes_num = meses.get(mes.lower())
    if mes_num:
        cantidad = movies[movies['release_date'].dt.month == mes_num].shape[0]
        return {"mes": mes, "cantidad": cantidad}
    else:
        return {"error": "Mes no válido"}

# Filmaciones por día
@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    dias = {
        "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
        "viernes": 4, "sábado": 5, "domingo": 6
    }
    dia_num = dias.get(dia.lower())
    if dia_num is not None:
        cantidad = movies[movies['release_date'].dt.dayofweek == dia_num].shape[0]
        return {"dia": dia, "cantidad": cantidad}
    else:
        return {"error": "Día no válido"}

# Título, año y score de una película
@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    pelicula = movies[movies['title'].str.contains(titulo, case=False, na=False)]
    if not pelicula.empty:
        return {
            "titulo": pelicula.iloc[0]['title'],
            "año": pelicula.iloc[0]['release_year'],
            "score": pelicula.iloc[0]['popularity']
        }
    else:
        return {"error": "Película no encontrada"}

# Votos por título
@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo: str):
    pelicula = movies[movies['title'].str.contains(titulo, case=False, na=False)]
    if not pelicula.empty:
        votos = pelicula.iloc[0]['vote_count']
        if votos >= 2000:
            return {
                "titulo": pelicula.iloc[0]['title'],
                "votos": votos,
                "promedio": pelicula.iloc[0]['vote_average']
            }
        else:
            return {"error": "La película no tiene suficientes votos"}
    else:
        return {"error": "Película no encontrada"}