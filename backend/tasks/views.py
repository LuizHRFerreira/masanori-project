"""
Camada HTTP — o "atendente" da API.

Cada função aqui recebe um request do Django e devolve uma resposta. O
trabalho delas é SÓ:
    1. olhar o método (GET, POST, PUT, DELETE);
    2. pegar os dados que vieram (query string na URL ou JSON no corpo);
    3. chamar a função certa do services.py;
    4. transformar o resultado (ou o erro) em resposta HTTP com o status certo.

Nada de regra de negócio aqui. Se a nota pode ir até 5 ou até 10, quem sabe
disso é o services.py, não o views.py.

Códigos de status usados:
    200 OK          -> deu certo (GET, PUT)
    201 Created     -> criou algo (POST)
    204 No Content  -> apagou, não tem nada para devolver (DELETE)
    400 Bad Request -> o cliente mandou dado inválido
    404 Not Found   -> o filme não existe
    405             -> método HTTP não suportado nessa URL
    503             -> o banco está fora do ar
"""
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import db, services


def health(request):
    """GET /api/health/ — o frontend usa para saber se o banco está de pé."""
    try:
        db.check_database()
        return JsonResponse({'status': 'ok', 'database': 'mongodb'})
    except Exception as error:
        return JsonResponse({'status': 'error', 'database': 'mongodb', 'detail': str(error)}, status=503)


# csrf_exempt: a API é chamada por JavaScript, sem formulário HTML nem cookie de
# sessão, então a proteção CSRF do Django não se aplica e só atrapalharia.
@csrf_exempt
def movies(request):
    """GET /api/movies/ lista (com busca e paginação); POST /api/movies/ cria."""
    if request.method == 'GET':
        try:
            # request.GET são os parâmetros da URL: ?q=drive&genre=Crime&page=2
            page = int(request.GET.get('page', '1'))
            page_size = int(request.GET.get('page_size', '20'))
            result = services.list_movies(
                request.GET.get('q', '').strip(),
                request.GET.get('genre', '').strip(),
                page,
                page_size,
            )
        except (TypeError, ValueError) as error:
            # int('abc') ou página negativa caem aqui.
            return JsonResponse({'detail': str(error)}, status=400)
        return JsonResponse(result)
    if request.method == 'POST':
        try:
            # request.body é o JSON cru enviado pelo frontend; json.loads vira dict.
            payload = json.loads(request.body)
            movie = services.create_movie(payload)
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON invalido.'}, status=400)
        except services.InvalidMovieError as error:
            # O services validou e não gostou (sem título, nota fora da faixa...).
            return JsonResponse({'detail': str(error)}, status=400)
        return JsonResponse(movie, status=201)
    return JsonResponse({'detail': 'Metodo nao permitido.'}, status=405)


def genres(request):
    """GET /api/genres/ — lista de gêneros distintos, para o filtro e o autocomplete."""
    if request.method != 'GET':
        return JsonResponse({'detail': 'Metodo nao permitido.'}, status=405)
    # safe=False porque a resposta é uma lista, não um dict (proteção antiga do Django).
    return JsonResponse(services.list_genres(), safe=False)


@csrf_exempt
def populate(request):
    """POST /api/movies/populate/ — apaga tudo e importa N filmes do Kaggle."""
    if request.method != 'POST':
        return JsonResponse({'detail': 'Metodo nao permitido.'}, status=405)
    try:
        payload = json.loads(request.body)
        amount = payload.get('amount')
        inserted = services.populate_movies(amount)
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON invalido.'}, status=400)
    except services.PopulationError as error:
        return JsonResponse({'detail': str(error)}, status=400)
    return JsonResponse({'inserted': inserted})


@csrf_exempt
def movie_detail(request, movie_id):
    """PUT /api/movies/<id>/ edita; DELETE /api/movies/<id>/ apaga.

    movie_id chega como string vinda da URL. Quem confere se é um ObjectId
    válido é o services.find_movie.
    """
    if request.method == 'DELETE':
        try:
            services.delete_movie(movie_id)
        except services.InvalidMovieIdError as error:
            return JsonResponse({'detail': str(error)}, status=400)
        except services.MovieNotFoundError as error:
            return JsonResponse({'detail': str(error)}, status=404)
        return HttpResponse(status=204)
    if request.method == 'PUT':
        try:
            payload = json.loads(request.body)
            movie = services.update_movie(movie_id, payload)
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON invalido.'}, status=400)
        except services.InvalidMovieIdError as error:
            return JsonResponse({'detail': str(error)}, status=400)
        except services.MovieNotFoundError as error:
            return JsonResponse({'detail': str(error)}, status=404)
        except services.InvalidMovieError as error:
            return JsonResponse({'detail': str(error)}, status=400)
        return JsonResponse(movie)
    return JsonResponse({'detail': 'Metodo nao permitido.'}, status=405)
