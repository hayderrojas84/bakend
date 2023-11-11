import json

from gym.models import Transactions, People
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def getTransactionsByPeopleId(request, people_id):
  if request.method == 'GET':
    transactions = Transactions.objects.filter(peopleId=people_id)
    
    data = [model_to_dict(transaction) for transaction in transactions]
    
    return JsonResponse(data, safe=False)
  else:
    return JsonResponse({'message': 'Metodo no permitido'})

@csrf_exempt
def create_transaction(request):
  if request.method == 'POST':
    request_body = request.body.decode('utf-8')
    try:
      transaction_data = json.loads(request_body)
      peopleId = transaction_data['peopleId']
      people = People.objects.get(pk=peopleId)
      
      new_transaction = Transactions(
        peopleId=people,
        startDate=transaction_data['startDate'],
        endDate=transaction_data['endDate'],
        value=transaction_data['value']
      )
      
      new_transaction.save()
      return JsonResponse({'message': 'Transacción creada', 'id': new_transaction.id}, status=201)
    except json.JSONDecodeError:
      return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
    except KeyError:
      return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    except People.DoesNotExist:
      return JsonResponse({'Persona no encontrada'}, status=404)
  else:
    return JsonResponse({'message': 'Metodo no permitido'})
  
def transaction_detail(request, transaction_id):
  if request.method == 'GET':
    try:
      transaction = Transactions.objects.get(pk=transaction_id)
      
      data = model_to_dict(transaction)
            
      return JsonResponse(data, safe=False)
    except Transactions.DoesNotExist:
      return JsonResponse({'Transacción no encontrada'}, status=404)
  else:
    return JsonResponse({'message': 'Metodo no permitido'})