"""
Configurações do Django.

Este projeto usa o Django SÓ como servidor HTTP (receber requests e devolver
JSON). Ele NÃO usa o ORM do Django (models.py, migrations) — quem fala com o
banco é o pymongo, direto, lá em tasks/db.py. Por isso as configurações aqui
são bem menores do que num projeto Django tradicional.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Pasta raiz do backend (a que contém manage.py).
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega o arquivo .env (se existir) para dentro das variáveis de ambiente.
# No Docker, as variáveis vêm do docker-compose.yml e o .env nem é usado.
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-secret-key')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# Hosts que o Django aceita atender. "backend" é o nome do container no compose.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# Apps instalados: o mínimo possível. 'tasks' é o nosso app (a API de filmes).
INSTALLED_APPS = ['django.contrib.contenttypes', 'corsheaders', 'tasks.apps.TasksConfig']

# CORS libera o navegador a chamar a API a partir de outra origem (o Vite em :5174).
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', 'django.middleware.common.CommonMiddleware']

# Arquivo que define as rotas. Começa em config/urls.py.
ROOT_URLCONF = 'config.urls'
TEMPLATES = []
WSGI_APPLICATION = 'config.wsgi.application'

# AQUI está a grande diferença: dizemos ao Django que ele NÃO tem banco
# relacional nenhum ('dummy'). O banco de verdade é o MongoDB, configurado abaixo.
DATABASES = {'default': {'ENGINE': 'django.db.backends.dummy'}}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:5174').split(',')

# Conexão com o MongoDB. No Docker, MONGO_URI aponta para o container "mongodb".
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'masanori')
