from datetime import datetime, timezone
from random import randint

from bson import ObjectId

from . import kaggle
from .db import movies as collection

MAX_POPULATE = 1000


# --- Erros ---------------------------------------------------------------
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
    return sorted(genre for genre in collection.distinct('genre') if genre)


def list_movies(query='', genre='', page=1, page_size=20):
    if not isinstance(page, int) or page < 1:
        raise ValueError('A pagina deve ser um numero inteiro positivo.')
    if not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise ValueError('O tamanho da pagina deve estar entre 1 e 100.')

    filters = {}
    if query:
        filters['$or'] = [
            {'title': {'$regex': query, '$options': 'i'}},
            {'director': {'$regex': query, '$options': 'i'}},
            {'tags': {'$regex': query, '$options': 'i'}},
        ]
    if genre:
        filters['genre'] = genre  

    total = collection.count_documents(filters)
    total_pages = max(1, (total + page_size - 1) // page_size)  
    page = min(page, total_pages)  

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
    movie = normalize_movie(payload)
    result = collection.insert_one(movie)
    movie['_id'] = result.inserted_id  
    return serialize(movie)


def update_movie(movie_id, payload):
    movie = find_movie(movie_id)
    updated = normalize_movie(payload)
    updated['created_at'] = movie['created_at']
    collection.replace_one({'_id': movie['_id']}, updated)
    updated['_id'] = movie['_id']
    return serialize(updated)


def delete_movie(movie_id):
    movie = find_movie(movie_id)
    collection.delete_one({'_id': movie['_id']})


def populate_movies(amount):
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
    collection.delete_many({})      
    collection.insert_many(selected) 
    return len(selected)


# --- Apoio ---------------------------------------------------------------

def find_movie(movie_id):
    try:
        object_id = ObjectId(movie_id)
    except Exception as error:
        raise InvalidMovieIdError('Id invalido.') from error
    movie = collection.find_one({'_id': object_id})
    if not movie:
        raise MovieNotFoundError('Filme nao encontrado.')
    return movie


def normalize_movie(payload):
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
