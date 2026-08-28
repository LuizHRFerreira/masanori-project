import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import services


def health(request):
    try:
        services.check_database()
        return JsonResponse({'status': 'ok', 'database': 'mongodb'})
    except Exception as error:
        return JsonResponse({'status': 'error', 'database': 'mongodb', 'detail': str(error)}, status=503)


@csrf_exempt
def books(request):
    if request.method == 'GET':
        try:
            page = int(request.GET.get('page', '1'))
            page_size = int(request.GET.get('page_size', '20'))
            result = services.list_books(
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
            book = services.create_book(payload)
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON invalido.'}, status=400)
        except services.InvalidBookError as error:
            return JsonResponse({'detail': str(error)}, status=400)
        return JsonResponse(book, status=201)
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
        inserted = services.populate_books(amount)
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON invalido.'}, status=400)
    except services.PopulationError as error:
        return JsonResponse({'detail': str(error)}, status=400)
    return JsonResponse({'inserted': inserted})


@csrf_exempt
def book_detail(request, book_id):
    if request.method == 'DELETE':
        try:
            services.delete_book(book_id)
        except services.InvalidBookIdError as error:
            return JsonResponse({'detail': str(error)}, status=400)
        except services.BookNotFoundError as error:
            return JsonResponse({'detail': str(error)}, status=404)
        return HttpResponse(status=204)
    if request.method == 'PUT':
        try:
            payload = json.loads(request.body)
            book = services.update_book(book_id, payload)
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON invalido.'}, status=400)
        except services.InvalidBookIdError as error:
            return JsonResponse({'detail': str(error)}, status=400)
        except services.BookNotFoundError as error:
            return JsonResponse({'detail': str(error)}, status=404)
        except services.InvalidBookError as error:
            return JsonResponse({'detail': str(error)}, status=400)
        return JsonResponse(book)
    return JsonResponse({'detail': 'Metodo nao permitido.'}, status=405)
