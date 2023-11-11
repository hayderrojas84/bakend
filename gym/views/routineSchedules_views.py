from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from gym.models import RoutineSchedules, People, Routines
import json

# Vista para listar todos los horarios de rutina (operación de lectura)
def routine_schedules_list(request):
    if request.method == 'GET':
        schedules = RoutineSchedules.objects.all()
        data = [model_to_dict(schedule) for schedule in schedules]
        return JsonResponse(data, safe=False)
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)
  
# Vista para listar todos los horarios de rutina (operación de lectura)
def routine_schedules_by_people_id(request, people_id):
    if request.method == 'GET':
        schedules = RoutineSchedules.objects.filter(peopleId=people_id)
        data = [model_to_dict(schedule) for schedule in schedules]
        return JsonResponse(data, safe=False)
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear un nuevo horario de rutina (operación de creación)
@csrf_exempt
def create_routine_schedule(request):
    if request.method == 'POST':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            schedule_data = json.loads(request_body)

            # Crear un nuevo horario de rutina a partir de los datos
            new_schedule = RoutineSchedules(
                peopleId=People.objects.get(pk=schedule_data['peopleId']),
                routineId=Routines.objects.get(pk=schedule_data['routineId']),
                dayOfWeek=schedule_data['dayOfWeek']
            )

            new_schedule.save()

            return JsonResponse({'message': 'Horario de rutina creado', 'id': new_schedule.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)

    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para obtener detalles de un horario de rutina (operación de lectura)
def routine_schedule_detail(request, schedule_id):
    try:
        schedule = RoutineSchedules.objects.get(pk=schedule_id)
    except RoutineSchedules.DoesNotExist:
        return JsonResponse({'message': 'Horario de rutina no encontrado'}, status=404)

    if request.method == 'GET':
        data = model_to_dict(schedule)
        return JsonResponse(data)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para actualizar un horario de rutina (operación de actualización)
@csrf_exempt
def update_routine_schedule(request, schedule_id):
    try:
        schedule = RoutineSchedules.objects.get(pk=schedule_id)
    except RoutineSchedules.DoesNotExist:
        return JsonResponse({'message': 'Horario de rutina no encontrado'}, status=404)

    if request.method == 'PUT':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            schedule_data = json.loads(request_body)

            # Actualizar los campos del horario de rutina con los datos proporcionados
            if 'dayOfWeek' in schedule_data:
                schedule.dayOfWeek = schedule_data['dayOfWeek']

            schedule.save()

            return JsonResponse({'message': 'Horario de rutina actualizado'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except RoutineSchedules.DoesNotExist:
            return JsonResponse({'message': 'Horario de rutina no encontrado'}, status=404)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para eliminar un horario de rutina (operación de eliminación)
def delete_routine_schedule(request, schedule_id):
    try:
        schedule = RoutineSchedules.objects.get(pk=schedule_id)
    except RoutineSchedules.DoesNotExist:
        return JsonResponse({'message': 'Horario de rutina no encontrado'}, status=404)

    if request.method == 'DELETE':
        schedule.delete()
        return JsonResponse({'message': 'Horario de rutina eliminado'})
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)
