from django.urls import path

from .views import genres, health, movie_detail, movies, populate

urlpatterns = [
    path('health/', health),
    path('movies/', movies),
    path('genres/', genres),
    path('movies/populate/', populate),
    path('movies/<str:movie_id>/', movie_detail),
]
