"""
Configuração do app "tasks".

O Django chama o método ready() uma vez, quando o servidor sobe. A gente
aproveita esse momento para garantir que o índice do MongoDB existe.
"""
from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        # Import aqui dentro (e não no topo) porque, na hora que o Django lê
        # este arquivo, as settings ainda não estão prontas — e db.py precisa delas.
        from . import db

        # create_index é idempotente: se o índice já existe, não faz nada.
        db.ensure_indexes()
