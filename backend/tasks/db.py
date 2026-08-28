"""
A "linha de telefone" com o MongoDB.

Tudo que precisa falar com o banco importa `movies` daqui. Nenhum outro
arquivo abre conexão por conta própria.

Vocabulário (relacional -> Mongo):
    banco   -> banco      (masanori)
    tabela  -> coleção    (movies)
    linha   -> documento  (um filme, em formato JSON/BSON)
    coluna  -> campo      (title, year, ...)
"""
from django.conf import settings
from pymongo import MongoClient

# Abre a conexão. serverSelectionTimeoutMS=2000 = espera no máximo 2s pelo
# banco antes de dar erro (em vez de travar para sempre).
client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)

# O banco "masanori"...
database = client[settings.MONGO_DB_NAME]

# ...e dentro dele a coleção "movies". No Mongo não é preciso "criar" a
# coleção: ela passa a existir no primeiro insert.
movies = database['movies']


def check_database():
    """Manda um 'ping' ao Mongo. Se ele não responder, levanta exceção."""
    client.admin.command('ping')


def ensure_indexes():
    """
    Cria o índice usado pela listagem.

    A listagem sempre ordena por created_at, do mais novo para o mais antigo.
    Sem índice, o Mongo lê TODOS os documentos e ordena na mão a cada request
    (COLLSCAN). Com o índice, a ordem já está pronta e ele pega só os 20 da
    página (IXSCAN). O -1 significa "decrescente".
    """
    movies.create_index([('created_at', -1)], name='created_at_desc')
