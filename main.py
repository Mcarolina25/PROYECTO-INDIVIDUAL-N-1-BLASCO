from fastapi import FastAPI, HTTPException
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Crear la estructura básica
app = FastAPI()

# Cargar el dataset procesado
movies = pd.read_csv('Movies/processed_movies_dataset.csv', low_memory=False)
credits= pd.read_csv('Movies/processed_credits_dataset.csv')

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

# Función para obtener información de un actor
@app.get("/actor/{nombre_actor}")
def get_actor(nombre_actor: str):
    # Filtrar las películas en las que ha participado el actor
    actor_movies = credits[credits['cast'].str.contains(nombre_actor, na=False)]
    
    if actor_movies.empty:
        raise HTTPException(status_code=404, detail="Actor no encontrado")

    cantidad_peliculas = len(actor_movies)
    total_revenue = actor_movies['revenue'].sum()
    promedio_revenue = total_revenue / cantidad_peliculas if cantidad_peliculas > 0 else 0

    return {
        "mensaje": f"El actor {nombre_actor} ha participado de {cantidad_peliculas} filmaciones.",
        "total_revenue": total_revenue,
        "promedio_revenue": promedio_revenue
    }

# Función para obtener información de un director
@app.get("/director/{nombre_director}")
def get_director(nombre_director: str):
    # Filtrar las películas dirigidas por el director
    director_movies = credits[credits['crew'].str.contains(nombre_director, na=False)]
    
    if director_movies.empty:
        raise HTTPException(status_code=404, detail="Director no encontrado")

    resultados = []
    for _, row in director_movies.iterrows():
        resultados.append({
            "titulo": row['title'],
            "fecha_lanzamiento": row['release_year'],
            "costo": row['budget'],
            "ganancia": row['revenue']
        })

    return {
        "director": nombre_director,
        "peliculas": resultados
    }    
# Generar una nube de palabras con los títulos de las películas
def generar_nube_palabras():
    plt.figure(figsize=(10, 5))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(movies['title'].dropna()))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('nube_palabras.png')  # Guarda la nube de palabras como imagen
    plt.close()

# Preprocesar los datos para la recomendación
tfidf = TfidfVectorizer(stop_words='english')
# Asegúrate de que 'genres' esté presente en el DataFrame
if 'genres' in movies.columns:
    movies['combined_features'] = movies['genres']  # Solo usando géneros para la recomendación
else:
    raise ValueError("La columna 'genres' no se encuentra en el DataFrame.")

tfidf_matrix = tfidf.fit_transform(movies['combined_features'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Función para obtener recomendaciones
@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
    if titulo not in movies['title'].values:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    # Obtener el índice de la película
    idx = movies.index[movies['title'] == titulo].tolist()[0]

    # Obtener las puntuaciones de similitud para todas las películas
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Ordenar las películas basadas en la puntuación de similitud
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Obtener las 5 películas más similares
    top_5_indices = [i[0] for i in sim_scores[1:6]]  # Excluye la película misma
    top_5_titles = movies['title'].iloc[top_5_indices].tolist()

    return {
        "peliculas_similares": top_5_titles
    }