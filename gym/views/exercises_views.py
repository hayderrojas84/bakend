from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from gym.models import Exercises, Machines, ExerciseMachines
import json
import base64
from PIL import Image
from io import BytesIO

# Vista para listar todos los ejercicios (operación de lectura)
def exercise_list(request):
    if request.method == 'GET':
        exercises = Exercises.objects.all()
        data = []
        for exercise in exercises:
          exerciseMachines = ExerciseMachines.objects.filter(exerciseId=exercise.id)
                    
          machines = []
          if len(exerciseMachines):
            for exm in exerciseMachines:
              machine = Machines.objects.get(pk=exm.machineId.id)
              machines.append(model_to_dict(machine))
              
          exercise_data = model_to_dict(exercise)
          
          exercise_data['machines'] = sorted(machines, key=lambda d: d['name'])
          
          image_data = None
          if exercise.image:
              image_data = base64.b64encode(exercise.image).decode('utf-8')

          exercise_data['image'] = f"data:image/jpeg;base64,{image_data}" if image_data else None
          data.append(exercise_data)

        return JsonResponse(data, safe=False)
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear un nuevo ejercicio (operación de creación)
@csrf_exempt
def create_exercise(request):
    if request.method == 'POST':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        try:
            data = {
                'exercise': json.loads(request.POST['exercise']),
                'machines': json.loads(request.POST['machines'])
            }
            # Analizar el JSON en un diccionario
            exercise_data = data['exercise']

            # Crear un nuevo ejercicio a partir de los datos
            new_exercise = Exercises(
                name=exercise_data['name'],
                muscleGroup=exercise_data['muscleGroup'],
                description=exercise_data.get('description', None)
            )
            
            image = request.FILES.get('image')
                
            if image:
                img = Image.open(image)
                img_bytes_io = BytesIO()
                img = img.convert('RGB')
                img.save(img_bytes_io, format='JPEG')
                new_exercise.image = img_bytes_io.getvalue()

            new_exercise.save()
            
            machines_ids = data['machines']
            
            for machineId in machines_ids:
              machine = Machines.objects.get(pk=machineId)
              ExerciseMachines.objects.get_or_create(exerciseId=new_exercise, machineId=machine)

            return JsonResponse({'message': 'Ejercicio creado', 'id': new_exercise.id}, status=201)
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

        image_data = None
        if exercise.image:
          image_data = base64.b64encode(exercise.image).decode('utf-8')

        data['image'] = f"data:image/jpeg;base64,{image_data}" if image_data else None
        
        exerciseMachines = ExerciseMachines.objects.filter(exerciseId=exercise.id)
                    
        machines = []
        if len(exerciseMachines):
            for exm in exerciseMachines:
              machine = Machines.objects.get(pk=exm.machineId.id)
              machines.append(model_to_dict(machine))
        
        data['machines'] = sorted(machines, key=lambda d: d['name'])

        return JsonResponse(data)
        
        return JsonResponse(data)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para actualizar un ejercicio (operación de actualización)
@csrf_exempt
def update_exercise(request, exercise_id):
    try:
        exercise = Exercises.objects.get(pk=exercise_id)
    except Exercises.DoesNotExist:
        return JsonResponse({'message': 'Ejercicio no encontrado'}, status=404)

    if request.method == 'POST':
        try:
            # Analizar el JSON en un diccionario
            data = {
                'exercise': json.loads(request.POST['exercise']),
                'machines': json.loads(request.POST['machines'])
            }
            
            exercise_data = data['exercise']

            # Actualizar los campos del ejercicio con los datos proporcionados
            if 'name' in exercise_data:
                exercise.name = exercise_data['name']
            if 'muscleGroup' in exercise_data:
                exercise.muscleGroup = exercise_data['muscleGroup']
            if 'description' in exercise_data:
                exercise.description = exercise_data.get('description', None)
                
            image = request.FILES.get('image')
                
            if image:
                img = Image.open(image)
                img_bytes_io = BytesIO()
                img = img.convert('RGB')
                img.save(img_bytes_io, format='JPEG')
                exercise.image = img_bytes_io.getvalue()

            exercise.save()
            
            machines_ids = data['machines']
            
            exerciseMachines = [exm.id for exm in ExerciseMachines.objects.filter(exerciseId=exercise.id)]
            
            currentExerciseMachines = []
            
            if len(machines_ids):
              for machineId in machines_ids:
                machine = Machines.objects.get(pk=machineId)
                exMach, create = ExerciseMachines.objects.get_or_create(exerciseId=exercise, machineId=machine)
                currentExerciseMachines.append(exMach.id)
                
              
            for exm in exerciseMachines:
              if len(currentExerciseMachines):
                if exm not in currentExerciseMachines:
                  ExerciseMachines.objects.get(pk=exm).delete()
              elif len(exerciseMachines):
                ExerciseMachines.objects.get(pk=exm).delete()
              
            return JsonResponse({'message': 'Ejercicio actualizado', 'id': exercise.id}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except Exercises.DoesNotExist:
            return JsonResponse({'message': 'Ejercicio no encontrado'}, status=404)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para eliminar un ejercicio (operación de eliminación)
@csrf_exempt
def delete_exercise(request, exercise_id):
    try:
        exercise = Exercises.objects.get(pk=exercise_id)
    except Exercises.DoesNotExist:
        return JsonResponse({'message': 'Ejercicio no encontrado'}, status=404)

    if request.method == 'DELETE':
        exercise.delete()
        return JsonResponse({'message': 'Ejercicio eliminado'})
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)
