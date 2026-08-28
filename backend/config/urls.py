"""
Portaria do projeto: toda URL que começa com /api/ é encaminhada para
tasks/urls.py, que decide qual função atende cada endereço.
"""
from django.urls import include, path

urlpatterns = [path('api/', include('tasks.urls'))]
