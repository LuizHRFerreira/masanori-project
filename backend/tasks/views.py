import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import db, services


def health(request):
    try:
        db.check_database()
        return JsonResponse({'status': 'ok', 'database': 'mongodb'})
    except Exception as error:
        return JsonResponse({'status': 'error', 'database': 'mongodb', 'detail': str(error)}, status=503)


@csrf_exempt
def movies(request):

    if request.method == 'GET':
        try:
            page = int(request.GET.get('page', '1'))
            page_size = int(request.GET.get('page_size', '20'))
            result = services.list_movies(
                request.GET.get('q', '').strip(),
                request.GET.get('genre', '').strip(),
                page,
                page_size,
            )
        except (TypeError, ValueError) as error:
            return JsonResponse({'detail': str(error)}, status=400)
        return JsonResponse(result)
    
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            movie = services.create_movie(payload)
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON invalido.'}, status=400)
        except services.InvalidMovieError as error:
            return JsonResponse({'detail': str(error)}, status=400)
        return JsonResponse(movie, status=201)
    return JsonResponse({'detail': 'Metodo nao permitido.'}, status=405)


def genres(request):
    if request.method != 'GET':
        return JsonResponse({'detail': 'Metodo nao permitido.'}, status=405)
    return JsonResponse(services.list_genres(), safe=False)


@csrf_exempt
def populate(request):
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
