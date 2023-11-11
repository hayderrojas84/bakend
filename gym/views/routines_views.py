from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from gym.models import Routines, RoutinesExercises, Exercises
import json

# Vista para listar todas las rutinas (operación de lectura)
def routine_list(request):
    if request.method == 'GET':
        goal = request.GET.get('goal')
        difficulty = request.GET.get('difficulty')
        muscleGroup = request.GET.get('muscleGroup')
                
        routines = Routines.objects.all()
        
        if goal:
            routines = routines.filter(goal=goal)
        if difficulty:
            routines = routines.filter(difficulty=difficulty)
        if muscleGroup:
            routines = routines.filter(muscleGroup=muscleGroup)

        data = []
        
        for routine in routines:
          routine_data = model_to_dict(routine)
          
          routineExercises = RoutinesExercises.objects.filter(routineId=routine.id)
          
          exercises = []
          
          if len(routineExercises):
            for routineExercise in routineExercises:
              exercise = Exercises.objects.get(pk=routineExercise.exerciseId.id)
              exercises.append(model_to_dict(exercise))

          routine_data['exercises'] = sorted(exercises, key=lambda d: d['name'])
          
          data.append(routine_data)
          
        return JsonResponse(data, safe=False)
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear una nueva rutina (operación de creación)
@csrf_exempt
def create_routine(request):
    if request.method == 'POST':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            data = json.loads(request_body)
            
            routine_data = data['routine']

            # Crear una nueva rutina a partir de los datos
            new_routine = Routines(
                name=routine_data['name'],
                description=routine_data.get('description', None),
                difficulty=routine_data.get('difficulty', 'Principiante'),
                goal=routine_data['goal'],
                muscleGroup=routine_data['muscleGroup']
            )

            new_routine.save()
            
            exercisesIds = data['exercises'] if 'exercises' in data else []
            
            if len(exercisesIds):
              for exerciseId in exercisesIds:
                exercise = Exercises.objects.get(pk=exerciseId)
                RoutinesExercises.objects.get_or_create(routineId=new_routine, exerciseId=exercise)

            return JsonResponse({'message': 'Rutina creada', 'id': new_routine.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)

    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para obtener detalles de una rutina (operación de lectura)
def routine_detail(request, routine_id):
    try:
        routine = Routines.objects.get(pk=routine_id)
    except Routines.DoesNotExist:
        return JsonResponse({'message': 'Rutina no encontrada'}, status=404)

    if request.method == 'GET':
        routineExercises = RoutinesExercises.objects.filter(routineId=routine.id)
        exercises = []
        if len(routineExercises):
          for routineExercise in routineExercises:
            exercise = Exercises.objects.get(pk=routineExercise.exerciseId.id)
            exercises.append(model_to_dict(exercise))
        data = model_to_dict(routine)
        data['exercises'] = sorted(exercises, key=lambda d: d['name'])
        return JsonResponse(data)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para actualizar una rutina (operación de actualización)
@csrf_exempt
def update_routine(request, routine_id):
    try:
        routine = Routines.objects.get(pk=routine_id)
    except Routines.DoesNotExist:
        return JsonResponse({'message': 'Rutina no encontrada'}, status=404)

    if request.method == 'PUT':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            data = json.loads(request_body)
            
            routine_data = data['routine']

            # Actualizar los campos de la rutina con los datos proporcionados
            if 'name' in routine_data:
                routine.name = routine_data['name']
            if 'description' in routine_data:
                routine.description = routine_data.get('description', None)
            if 'difficulty' in routine_data:
                routine.difficulty = routine_data.get('difficulty', 'Principiante')
            if 'goal' in routine_data:
                routine.goal = routine_data['goal']
            if 'muscleGroup' in routine_data:
                routine.muscleGroup = routine_data['muscleGroup']

            routine.save()
            
            exercisesIds = data['exercises'] if 'exercises' in data else []
            
            routineExercises = [exm.id for exm in RoutinesExercises.objects.filter(routineId=routine.id)]

            currentRoutineExercises = []
            
            if len(exercisesIds):
              for exerciseId in exercisesIds:
                exercise = Exercises.objects.get(pk=exerciseId)
                exExercise, create = RoutinesExercises.objects.get_or_create(routineId=routine, exerciseId=exercise)
                currentRoutineExercises.append(exExercise.id)
                
              
            for exExercises in routineExercises:
              if len(currentRoutineExercises):
                if exExercises not in currentRoutineExercises:
                  RoutinesExercises.objects.get(pk=exExercises).delete()
              elif len(routineExercises):
                RoutinesExercises.objects.get(pk=exExercises).delete()


            return JsonResponse({'message': 'Rutina actualizada'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except Routines.DoesNotExist:
            return JsonResponse({'message': 'Rutina no encontrada'}, status=404)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para eliminar una rutina (operación de eliminación)
@csrf_exempt
def delete_routine(request, routine_id):
    try:
        routine = Routines.objects.get(pk=routine_id)
    except Routines.DoesNotExist:
        return JsonResponse({'message': 'Rutina no encontrada'}, status=404)

    if request.method == 'DELETE':
        routine.delete()
        return JsonResponse({'message': 'Rutina eliminada'})
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)
