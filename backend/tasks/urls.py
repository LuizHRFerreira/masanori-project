"""
Lista de ramais da API: qual URL chama qual função do views.py.

    /api/health/            -> health        (o banco está no ar?)
    /api/movies/            -> movies        (GET lista / POST cria)
    /api/genres/            -> genres        (lista de gêneros existentes)
    /api/movies/populate/   -> populate      (importa filmes do Kaggle)
    /api/movies/<id>/       -> movie_detail  (PUT edita / DELETE apaga)

A ordem importa: 'movies/populate/' vem ANTES de 'movies/<str:movie_id>/',
senão o Django acharia que "populate" é um id de filme.
"""
from django.urls import path

from .views import genres, health, movie_detail, movies, populate

urlpatterns = [
    path('health/', health),
    path('movies/', movies),
    path('genres/', genres),
    path('movies/populate/', populate),
    path('movies/<str:movie_id>/', movie_detail),
]
