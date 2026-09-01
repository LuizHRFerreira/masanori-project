import csv
from datetime import datetime, timezone
from io import BytesIO, TextIOWrapper
from random import random
from urllib.request import urlopen
from zipfile import ZipFile

DATASET_URL = 'https://www.kaggle.com/api/v1/datasets/download/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows'

AVAILABLE_RATIO = 0.75


class DatasetError(ValueError):
    pass


def load_movies():
    try:
        with urlopen(DATASET_URL, timeout=30) as response:
            archive_data = response.read()
        with ZipFile(BytesIO(archive_data)) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith('.csv')]
            if not csv_names:
                raise DatasetError('O arquivo do Kaggle nao contem um CSV.')
            with archive.open(csv_names[0]) as csv_file:
                rows = csv.DictReader(TextIOWrapper(csv_file, encoding='utf-8-sig'))
                movies = [normalize_row(row) for row in rows]
    except DatasetError:
        raise
    except Exception as error:
        raise DatasetError('Nao foi possivel acessar a base de filmes do Kaggle.') from error

    movies = [movie for movie in movies if movie]  # descarta linhas sem título
    if not movies:
        raise DatasetError('Nao foi encontrado nenhum filme valido no dataset.')
    return movies


def normalize_row(row):
    title = column(row, 'series_title', 'title', 'name')
    if not title:
        return None
    genres = [genre.strip() for genre in column(row, 'genre', 'genres').split(',') if genre.strip()]
    certificate = column(row, 'certificate')

    movie = {key.strip().lower(): (value or '').strip() for key, value in row.items() if key}

    movie.update({
        'title': title,
        'director': column(row, 'director', 'directors'),
        'year': parse_year(column(row, 'released_year', 'year')),
        'genre': genres[0] if genres else 'Outros',            
        'tags': genres + ([certificate] if certificate else []),  
        'rating': parse_rating(column(row, 'imdb_rating', 'rating'), scale=10),
        'available': random() < AVAILABLE_RATIO,
        'created_at': datetime.now(timezone.utc),
    })
    return movie


def column(row, *names):
    normalized = {key.strip().lower().replace(' ', '_'): value for key, value in row.items()}
    for name in names:
        value = normalized.get(name)
        if value and value.strip():
            return value.strip()
    return ''


def parse_year(value):
    try:
        return int(value[-4:]) if value else None
    except (TypeError, ValueError):
        return None


def parse_rating(value, scale=5):
    try:
        rating = float(value) if value else None
        if rating is None or not 0 <= rating <= scale:
            return None
        return round(rating * 5 / scale, 1)
    except (TypeError, ValueError):
        return None
