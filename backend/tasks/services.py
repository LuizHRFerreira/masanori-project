"""
O "cérebro" da API: regras de negócio do acervo.

Aqui ficam validação, CRUD, busca, paginação e serialização. Este arquivo NÃO
sabe o que é HTTP — recebe e devolve dicts Python. Quem traduz para
request/response é o views.py.

Sobre validação: num banco relacional, a própria tabela garante que "year é
inteiro" ou "title não é nulo". O Mongo aceita qualquer coisa, então essa
responsabilidade vem para cá (normalize_movie). É o preço da flexibilidade.

Formato de um documento na coleção "movies":
    {
      "_id": ObjectId("6a91b974..."),   # gerado pelo Mongo
      "title": "Drive",
      "director": "Nicolas Winding Refn",
      "year": 2011,
      "genre": "Crime",
      "tags": ["neo-noir", "road movie"],
      "rating": 4.5,                    # 0 a 5
      "available": True,                # na prateleira (True) ou alugado (False)
      "created_at": datetime(...)
      # filmes importados do Kaggle ainda têm overview, star1, runtime, ...
    }
"""
from datetime import datetime, timezone
from random import randint

from bson import ObjectId

from . import kaggle
from .db import movies as collection

MAX_POPULATE = 1000


# --- Erros ---------------------------------------------------------------
# São "etiquetas": o services levanta a etiqueta certa e o views lê a etiqueta
# para escolher o código HTTP (400, 404...).

class InvalidMovieError(ValueError):
    """Os dados do filme não passaram na validação (-> 400)."""


class InvalidMovieIdError(ValueError):
    """O id não tem o formato de um ObjectId (-> 400)."""


class MovieNotFoundError(LookupError):
    """Não existe filme com esse id (-> 404)."""


class PopulationError(ValueError):
    """Problema ao importar do Kaggle (-> 400)."""


# --- Leitura -------------------------------------------------------------

def list_genres():
    """Gêneros distintos que existem hoje na coleção, em ordem alfabética.

    distinct('genre') é o equivalente de SELECT DISTINCT genre FROM movies.
    """
    return sorted(genre for genre in collection.distinct('genre') if genre)


def list_movies(query='', genre='', page=1, page_size=20):
    """
    Lista paginada, com busca por texto e filtro de gênero.

    Equivalente aproximado em SQL:
        SELECT * FROM movies
        WHERE (title ILIKE %q% OR director ILIKE %q% OR tags ILIKE %q%)
          AND genre = :genre
        ORDER BY created_at DESC
        LIMIT :page_size OFFSET (:page - 1) * :page_size
    """
    if not isinstance(page, int) or page < 1:
        raise ValueError('A pagina deve ser um numero inteiro positivo.')
    if not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise ValueError('O tamanho da pagina deve estar entre 1 e 100.')

    # O filtro do Mongo é um dict. {} vazio = "todos os documentos".
    filters = {}
    if query:
        # $or = qualquer uma das condições. $regex com $options 'i' = "contém,
        # ignorando maiúsculas". Em "tags" (que é uma lista) o Mongo testa
        # cada item da lista automaticamente.
        filters['$or'] = [
            {'title': {'$regex': query, '$options': 'i'}},
            {'director': {'$regex': query, '$options': 'i'}},
            {'tags': {'$regex': query, '$options': 'i'}},
        ]
    if genre:
        filters['genre'] = genre  # igualdade exata

    total = collection.count_documents(filters)
    total_pages = max(1, (total + page_size - 1) // page_size)  # arredonda para cima
    page = min(page, total_pages)  # se pediram a página 99 e só existem 3, devolve a 3

    # sort(-1) = decrescente (mais novos primeiro). skip/limit fazem a paginação.
    # É esse sort que o índice created_at_desc (db.py) acelera.
    results = collection.find(filters).sort('created_at', -1).skip((page - 1) * page_size).limit(page_size)
    return {
        'results': [serialize(movie) for movie in results],
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
    }


# --- Escrita -------------------------------------------------------------

def create_movie(payload):
    """Valida e insere. Devolve o filme já com o id gerado pelo Mongo."""
    movie = normalize_movie(payload)
    result = collection.insert_one(movie)
    movie['_id'] = result.inserted_id  # o Mongo cria o _id na hora do insert
    return serialize(movie)


def update_movie(movie_id, payload):
    """
    Edita um filme. replace_one troca o documento INTEIRO pelo novo (não é um
    "patch" campo a campo), por isso o frontend sempre manda todos os campos.
    Só o created_at original é preservado, para o filme não mudar de posição
    na listagem.
    """
    movie = find_movie(movie_id)
    updated = normalize_movie(payload)
    updated['created_at'] = movie['created_at']
    collection.replace_one({'_id': movie['_id']}, updated)
    updated['_id'] = movie['_id']
    return serialize(updated)


def delete_movie(movie_id):
    """Apaga um filme. find_movie garante que ele existe (senão -> 404)."""
    movie = find_movie(movie_id)
    collection.delete_one({'_id': movie['_id']})


def populate_movies(amount):
    """
    Zera o acervo e importa `amount` filmes do Kaggle.

    Escolhe um trecho aleatório da lista (start:start+amount) para que cada
    importação traga filmes diferentes.
    """
    # isinstance(amount, bool) porque em Python True == 1 e passaria na checagem.
    if not isinstance(amount, int) or isinstance(amount, bool) or not 1 <= amount <= MAX_POPULATE:
        raise PopulationError(f'A quantidade deve ser um numero inteiro entre 1 e {MAX_POPULATE}.')
    try:
        movies = kaggle.load_movies()
    except kaggle.DatasetError as error:
        raise PopulationError(str(error)) from error
    if len(movies) < amount:
        raise PopulationError('A base do Kaggle nao possui filmes suficientes.')

    start = randint(0, len(movies) - amount)
    selected = movies[start:start + amount]
    collection.delete_many({})       # {} = apaga TODOS os documentos
    collection.insert_many(selected)  # insere a lista de uma vez só
    return len(selected)


# --- Apoio ---------------------------------------------------------------

def find_movie(movie_id):
    """
    Busca um filme pelo id vindo da URL (string).

    O _id do Mongo é um ObjectId, não uma string; por isso a conversão. Se a
    string não tiver o formato certo (24 caracteres hexadecimais), ObjectId()
    levanta exceção e viramos isso em InvalidMovieIdError.
    """
    try:
        object_id = ObjectId(movie_id)
    except Exception as error:
        raise InvalidMovieIdError('Id invalido.') from error
    movie = collection.find_one({'_id': object_id})
    if not movie:
        raise MovieNotFoundError('Filme nao encontrado.')
    return movie


def normalize_movie(payload):
    """
    O validador. Recebe o dict cru vindo do JSON e devolve um documento limpo
    e consistente — ou levanta InvalidMovieError explicando o problema.

    Regras:
      - title é obrigatório;
      - year, se vier, tem que ser inteiro;
      - rating, se vier, tem que ser número entre 0 e 5;
      - tags pode vir como lista OU como string "a, b, c" (vira lista);
      - genre vazio vira "Outros";
      - available vira bool (padrão True).
    """
    if not isinstance(payload, dict):
        raise InvalidMovieError('JSON invalido.')
    title = str(payload.get('title', '')).strip()
    if not title:
        raise InvalidMovieError('O titulo e obrigatorio.')

    raw_tags = payload.get('tags', [])
    tags = [tag.strip() for tag in (raw_tags.split(',') if isinstance(raw_tags, str) else raw_tags) if tag.strip()]

    return {
        'title': title,
        'director': str(payload.get('director', '')).strip(),
        'year': parse_year(payload.get('year')),
        'genre': str(payload.get('genre', 'Outros')).strip() or 'Outros',
        'tags': tags,
        'rating': parse_rating(payload.get('rating')),
        'available': bool(payload.get('available', True)),
        'created_at': datetime.now(timezone.utc),
    }


def parse_year(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise InvalidMovieError('O ano deve ser um numero inteiro.') from error


def parse_rating(value):
    if value in (None, ''):
        return None
    try:
        rating = float(value)
    except (TypeError, ValueError) as error:
        raise InvalidMovieError('A nota deve ser um numero entre 0 e 5.') from error
    if not 0 <= rating <= 5:
        raise InvalidMovieError('A nota deve ser um numero entre 0 e 5.')
    return rating


def serialize(movie):
    """
    Converte um documento do Mongo em um dict pronto para virar JSON.

    Dois tipos do Mongo não existem em JSON e precisam de tradução:
      - ObjectId  -> string   ("_id" vira "id")
      - datetime  -> string ISO ("2026-08-28T16:38:12+00:00")

    Também escolhe SÓ os campos que o frontend usa. Os campos extras dos
    filmes importados (overview, star1...) ficam no banco, mas não trafegam.
    """
    return {
        'id': str(movie['_id']),
        'title': movie['title'],
        'director': movie.get('director', ''),
        'year': movie.get('year'),
        'genre': movie.get('genre', ''),
        'tags': movie.get('tags', []),
        'rating': movie.get('rating'),
        'available': movie.get('available', True),
        'created_at': movie['created_at'].isoformat(),
    }
