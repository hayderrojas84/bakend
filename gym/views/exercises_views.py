from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from gym.models import Exercises
import json

# Vista para listar todos los ejercicios (operación de lectura)
def exercise_list(request):
    if request.method == 'GET':
        exercises = Exercises.objects.all()
        data = [model_to_dict(exercise) for exercise in exercises]
        return JsonResponse(data, safe=False)
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear un nuevo ejercicio (operación de creación)
@csrf_exempt
def create_exercise(request):
    if request.method == 'POST':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            exercise_data = json.loads(request_body)

            # Crear un nuevo ejercicio a partir de los datos
            new_exercise = Exercises(
                name=exercise_data['name'],
                muscleGroup=exercise_data['muscleGroup'],
                description=exercise_data.get('description', None)
            )

            new_exercise.save()

            return JsonResponse({'message': 'Ejercicio creado'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)

    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para obtener detalles de un ejercicio (operación de lectura)
def exercise_detail(request, exercise_id):
    try:
        exercise = Exercises.objects.get(pk=exercise_id)
    except Exercises.DoesNotExist:
        return JsonResponse({'message': 'Ejercicio no encontrado'}, status=404)

    if request.method == 'GET':
        data = model_to_dict(exercise)
        return JsonResponse(data)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para actualizar un ejercicio (operación de actualización)
@csrf_exempt
def update_exercise(request, exercise_id):
    try:
        exercise = Exercises.objects.get(pk=exercise_id)
    except Exercises.DoesNotExist:
        return JsonResponse({'message': 'Ejercicio no encontrado'}, status=404)

    if request.method == 'PUT':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            exercise_data = json.loads(request_body)

            # Actualizar los campos del ejercicio con los datos proporcionados
            if 'name' in exercise_data:
                exercise.name = exercise_data['name']
            if 'muscleGroup' in exercise_data:
                exercise.muscleGroup = exercise_data['muscleGroup']
            if 'description' in exercise_data:
                exercise.description = exercise_data.get('description', None)

            exercise.save()

            return JsonResponse({'message': 'Ejercicio actualizado'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except Exercises.DoesNotExist:
            return JsonResponse({'message': 'Ejercicio no encontrado'}, status=404)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para eliminar un ejercicio (operación de eliminación)
def delete_exercise(request, exercise_id):
    try:
        exercise = Exercises.objects.get(pk=exercise_id)
    except Exercises.DoesNotExist:
        return JsonResponse({'message': 'Ejercicio no encontrado'}, status=404)

    if request.method == 'DELETE':
        exercise.delete()
        return JsonResponse({'message': 'Ejercicio eliminado'})
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)
