from django.urls import path
from .views import book_detail, books, health, populate
from .views import book_detail, books, genres, health, populate

urlpatterns = [
  path('health/', health),
  path('books/', books),
  path('genres/', genres),
  path('books/populate/', populate),
  path('books/<str:book_id>/', book_detail)
]
