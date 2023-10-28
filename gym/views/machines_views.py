from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from gym.models import Machines
import json


# Vista para listar todas las máquinas (operación de lectura)
def machine_list(request):
    if request.method == 'GET':
        machines = Machines.objects.all()
        data = [model_to_dict(machine) for machine in machines]
        return JsonResponse(data, safe=False)
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear una nueva máquina (operación de creación)
@csrf_exempt
def create_machine(request):
    if request.method == 'POST':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            machine_data = json.loads(request_body)

            # Crear una nueva máquina a partir de los datos
            new_machine = Machines(
                name=machine_data['name'],
                description=machine_data.get('description', None),
                muscleGroup=machine_data['muscleGroup'],
                quantity=machine_data.get('quantity', 1)
            )

            new_machine.save()

            return JsonResponse({'message': 'Máquina creada'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)

    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para obtener detalles de una máquina (operación de lectura)
def machine_detail(request, machine_id):
    try:
        machine = Machines.objects.get(pk=machine_id)
    except Machines.DoesNotExist:
        return JsonResponse({'message': 'Máquina no encontrada'}, status=404)

    if request.method == 'GET':
        data = model_to_dict(machine)
        return JsonResponse(data)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para actualizar una máquina (operación de actualización)
@csrf_exempt
def update_machine(request, machine_id):
    try:
        machine = Machines.objects.get(pk=machine_id)
    except Machines.DoesNotExist:
        return JsonResponse({'message': 'Máquina no encontrada'}, status=404)

    if request.method == 'PUT':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            machine_data = json.loads(request_body)

            # Actualizar los campos de la máquina con los datos proporcionados
            if 'name' in machine_data:
                machine.name = machine_data['name']
            if 'description' in machine_data:
                machine.description = machine_data.get('description', None)
            if 'muscleGroup' in machine_data:
                machine.muscleGroup = machine_data['muscleGroup']
            if 'quantity' in machine_data:
                machine.quantity = machine_data.get('quantity', 1)

            machine.save()

            return JsonResponse({'message': 'Máquina actualizada'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except Machines.DoesNotExist:
            return JsonResponse({'message': 'Máquina no encontrada'}, status=404)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para eliminar una máquina (operación de eliminación)
def delete_machine(request, machine_id):
    try:
        machine = Machines.objects.get(pk=machine_id)
    except Machines.DoesNotExist:
        return JsonResponse({'message': 'Máquina no encontrada'}, status=404)

    if request.method == 'DELETE':
        machine.delete()
        return JsonResponse({'message': 'Máquina eliminada'})
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)
