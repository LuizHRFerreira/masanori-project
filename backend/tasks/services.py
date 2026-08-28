from datetime import datetime, timezone
from io import BytesIO, TextIOWrapper
from random import randint
from urllib.request import urlopen
from zipfile import ZipFile

from bson import ObjectId
from django.conf import settings
from pymongo import MongoClient

client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
collection = client[settings.MONGO_DB_NAME]['books']
KAGGLE_DATASET_URL = 'https://www.kaggle.com/api/v1/datasets/download/abdallahwagih/books-dataset'


class InvalidBookError(ValueError):
    pass


class InvalidBookIdError(ValueError):
    pass


class BookNotFoundError(LookupError):
    pass


class PopulationError(ValueError):
    pass


def check_database():
    client.admin.command('ping')


def ensure_indexes():
    collection.create_index([('created_at', -1)], name='created_at_desc')

def list_genres():
    return sorted(genre for genre in collection.distinct('genre') if genre)


def list_books(query='', genre='', page=1, page_size=20):
    if not isinstance(page, int) or page < 1:
        raise ValueError('A pagina deve ser um numero inteiro positivo.')
    if not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise ValueError('O tamanho da pagina deve estar entre 1 e 100.')
    filters = {}
    if query:
        filters['$or'] = [
            {'title': {'$regex': query, '$options': 'i'}},
            {'author': {'$regex': query, '$options': 'i'}},
            {'tags': {'$regex': query, '$options': 'i'}},
        ]
    if genre:
        filters['genre'] = genre
    total = collection.count_documents(filters)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, total_pages)
    books = collection.find(filters).sort('created_at', -1).skip((page - 1) * page_size).limit(page_size)
    return {
        'results': [serialize(book) for book in books],
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
    }


def create_book(payload):
    title = get_title(payload)
    book = normalize_book(payload, title)
    result = collection.insert_one(book)
    book['_id'] = result.inserted_id
    return serialize(book)


def update_book(book_id, payload):
    book = find_book(book_id)
    title = get_title(payload)
    updated = normalize_book(payload, title)
    updated['created_at'] = book['created_at']
    collection.replace_one({'_id': book['_id']}, updated)
    updated['_id'] = book['_id']
    return serialize(updated)


def delete_book(book_id):
    book = find_book(book_id)
    collection.delete_one({'_id': book['_id']})


def populate_books(amount):
    if not isinstance(amount, int) or isinstance(amount, bool) or not 1 <= amount <= 1000:
        raise PopulationError('A quantidade deve ser um numero inteiro entre 1 e 1000.')

    books = load_kaggle_books()
    if len(books) < amount:
        raise PopulationError('A base do Kaggle nao possui livros suficientes.')

    start = randint(0, len(books) - amount)
    selected_books = books[start:start + amount]
    collection.delete_many({})
    collection.insert_many(selected_books)
    return len(selected_books)


def load_kaggle_books():
    try:
        with urlopen(KAGGLE_DATASET_URL, timeout=30) as response:
            archive_data = response.read()
        with ZipFile(BytesIO(archive_data)) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith('.csv')]
            if not csv_names:
                raise PopulationError('O arquivo do Kaggle nao contem um CSV.')
            with archive.open(csv_names[0]) as csv_file:
                import csv
                rows = csv.DictReader(TextIOWrapper(csv_file, encoding='utf-8-sig'))
                books = [normalize_dataset_book(row) for row in rows]
    except PopulationError:
        raise
    except Exception as error:
        raise PopulationError('Nao foi possivel acessar a base de livros do Kaggle.') from error

    books = [book for book in books if book]
    if not books:
        raise PopulationError('Nao foi encontrado nenhum livro valido no dataset.')
    return books


def normalize_dataset_book(row):
    title = dataset_value(row, 'title', 'name')
    if not title:
        return None
    author = dataset_value(row, 'authors', 'author', 'writer')
    genre = dataset_value(row, 'genre', 'genres', 'category', 'categories') or 'Outros'
    year = extract_year(dataset_value(row, 'publication_date', 'published_year', 'year'))
    rating = extract_rating(dataset_value(row, 'average_rating', 'rating', 'book_rating'))
    tags = [value for value in [dataset_value(row, 'language_code', 'language'), genre] if value]
    book = {key.strip(): (value or '').strip() for key, value in row.items() if key}
    book.update({
        'title': title,
        'author': author,
        'year': year,
        'genre': genre,
        'tags': tags,
        'rating': rating,
        'created_at': datetime.now(timezone.utc),
    })
    return book


def dataset_value(row, *names):
    normalized = {key.strip().lower().replace(' ', '_'): value for key, value in row.items()}
    for name in names:
        value = normalized.get(name)
        if value and value.strip():
            return value.strip()
    return ''


def extract_year(value):
    try:
        return int(value[-4:]) if value else None
    except (TypeError, ValueError):
        return None


def extract_rating(value):
    try:
        rating = float(value) if value else None
        return rating if rating is not None and 0 <= rating <= 5 else None
    except (TypeError, ValueError):
        return None


def find_book(book_id):
    try:
        object_id = ObjectId(book_id)
    except Exception as error:
        raise InvalidBookIdError('Id invalido.') from error
    book = collection.find_one({'_id': object_id})
    if not book:
        raise BookNotFoundError('Livro nao encontrado.')
    return book


def get_title(payload):
    try:
        title = payload.get('title', '').strip()
    except AttributeError as error:
        raise InvalidBookError('JSON invalido.') from error
    if not title:
        raise InvalidBookError('O titulo e obrigatorio.')
    return title


def normalize_book(payload, title):
    raw_tags = payload.get('tags', [])
    tags = [tag.strip() for tag in (raw_tags.split(',') if isinstance(raw_tags, str) else raw_tags) if tag.strip()]
    raw_rating = payload.get('rating')
    if raw_rating in (None, ''):
        rating = None
    else:
        try:
            rating = float(raw_rating)
        except (TypeError, ValueError) as error:
            raise InvalidBookError('A nota deve ser um numero entre 0 e 5.') from error
        if not 0 <= rating <= 5:
            raise InvalidBookError('A nota deve ser um numero entre 0 e 5.')
    return {
        'title': title,
        'author': str(payload.get('author', '')).strip(),
        'year': payload.get('year') or None,
        'genre': str(payload.get('genre', 'Outros')).strip() or 'Outros',
        'tags': tags,
        'rating': rating,
        'created_at': datetime.now(timezone.utc),
    }


def serialize(book):
    return {
        'id': str(book['_id']),
        'title': book['title'],
        'author': book.get('author', ''),
        'year': book.get('year'),
        'genre': book.get('genre', ''),
        'tags': book.get('tags', []),
        'rating': book.get('rating'),
        'created_at': book['created_at'].isoformat(),
    }
