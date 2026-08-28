"""
O importador: baixa o dataset "IMDB Top 1000" do Kaggle e transforma cada
linha do CSV em um documento no formato do nosso acervo.

Fica num arquivo separado porque é a única parte do backend que fala com o
mundo externo. Se o Kaggle mudar o formato do CSV, só este arquivo muda.

Fluxo: baixa um ZIP -> abre o CSV que está dentro -> para cada linha,
normalize_row() monta o documento.
"""
import csv
from datetime import datetime, timezone
from io import BytesIO, TextIOWrapper
from random import random
from urllib.request import urlopen
from zipfile import ZipFile

DATASET_URL = 'https://www.kaggle.com/api/v1/datasets/download/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows'

# Proporção de filmes sorteados como "disponíveis" (os outros ficam "alugados"),
# só para a tela mostrar os dois estados.
AVAILABLE_RATIO = 0.75


class DatasetError(ValueError):
    """Qualquer problema ao baixar ou ler o dataset."""


def load_movies():
    """Baixa o dataset e devolve uma lista de documentos prontos para inserir."""
    try:
        # Baixa o ZIP inteiro para a memória (tem ~180 KB, tranquilo).
        with urlopen(DATASET_URL, timeout=30) as response:
            archive_data = response.read()
        with ZipFile(BytesIO(archive_data)) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith('.csv')]
            if not csv_names:
                raise DatasetError('O arquivo do Kaggle nao contem um CSV.')
            with archive.open(csv_names[0]) as csv_file:
                # DictReader lê cada linha como um dict {nome_da_coluna: valor}.
                # utf-8-sig ignora o "BOM" que alguns CSVs trazem no início.
                rows = csv.DictReader(TextIOWrapper(csv_file, encoding='utf-8-sig'))
                movies = [normalize_row(row) for row in rows]
    except DatasetError:
        raise
    except Exception as error:
        # Sem internet, Kaggle fora do ar, ZIP corrompido... tudo vira um erro só.
        raise DatasetError('Nao foi possivel acessar a base de filmes do Kaggle.') from error

    movies = [movie for movie in movies if movie]  # descarta linhas sem título
    if not movies:
        raise DatasetError('Nao foi encontrado nenhum filme valido no dataset.')
    return movies


def normalize_row(row):
    """
    Transforma uma linha do CSV em um documento do acervo.

    O CSV tem colunas como Series_Title, Released_Year, Genre, Director,
    IMDB_Rating, Certificate, Runtime, Overview, Star1..Star4...
    """
    title = column(row, 'series_title', 'title', 'name')
    if not title:
        return None
    # "Action, Crime, Drama" -> ['Action', 'Crime', 'Drama']
    genres = [genre.strip() for genre in column(row, 'genre', 'genres').split(',') if genre.strip()]
    certificate = column(row, 'certificate')

    # Começa copiando TODAS as colunas do CSV (com nomes em minúsculo). É isso
    # que faz um filme importado ter sinopse, elenco, bilheteria etc., enquanto
    # um cadastrado à mão tem só os campos básicos — o esquema flexível do Mongo.
    movie = {key.strip().lower(): (value or '').strip() for key, value in row.items() if key}

    # Por cima, os campos padronizados que a aplicação realmente usa.
    movie.update({
        'title': title,
        'director': column(row, 'director', 'directors'),
        'year': parse_year(column(row, 'released_year', 'year')),
        'genre': genres[0] if genres else 'Outros',            # o primeiro vira o gênero principal
        'tags': genres + ([certificate] if certificate else []),  # todos + classificação viram tags
        'rating': parse_rating(column(row, 'imdb_rating', 'rating'), scale=10),
        'available': random() < AVAILABLE_RATIO,
        'created_at': datetime.now(timezone.utc),
    })
    return movie


def column(row, *names):
    """
    Pega o valor da primeira coluna que existir entre os nomes dados.

    Ignora maiúsculas e troca espaço por "_", então 'Series Title',
    'series_title' e 'SERIES_TITLE' são tratados como a mesma coluna.
    """
    normalized = {key.strip().lower().replace(' ', '_'): value for key, value in row.items()}
    for name in names:
        value = normalized.get(name)
        if value and value.strip():
            return value.strip()
    return ''


def parse_year(value):
    """'1994' -> 1994. Pega os 4 últimos caracteres para tolerar '12/03/1994'."""
    try:
        return int(value[-4:]) if value else None
    except (TypeError, ValueError):
        return None


def parse_rating(value, scale=5):
    """Converte a nota para a escala 0-5 (a do IMDB vai de 0 a 10: 9.3 -> 4.7)."""
    try:
        rating = float(value) if value else None
        if rating is None or not 0 <= rating <= scale:
            return None
        return round(rating * 5 / scale, 1)
    except (TypeError, ValueError):
        return None
