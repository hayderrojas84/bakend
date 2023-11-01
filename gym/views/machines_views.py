from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from PIL import Image
from io import BytesIO
import json
import base64

from gym.models import Machines


# Vista para listar todas las máquinas (operación de lectura)
def machine_list(request):
    if request.method == 'GET':
        machines = Machines.objects.all()
        data = []

        for machine in machines:
            image_data = None
            if machine.image:
                image_data = base64.b64encode(machine.image).decode('utf-8')
            
            data.append({
                'id': machine.id,
                'name': machine.name,
                'description': machine.description,
                'muscleGroup': machine.muscleGroup,
                'quantity': machine.quantity,
                'image': f"data:image/jpeg;base64,{image_data}" if image_data else None
            })

        return JsonResponse(data, safe=False)

    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear una nueva máquina (operación de creación)
@csrf_exempt
def create_machine(request):
    if request.method == 'POST':
        try:
            # Filtra los campos de la solicitud POST
            machine_data = {
                'name': request.POST.get('name', ''),
                'description': request.POST.get('description', None),
                'muscleGroup': request.POST.get('muscleGroup', ''),
                'quantity': int(request.POST.get('quantity', 1))
            }
            
            new_machine = Machines(
                name=machine_data['name'],
                description=machine_data['description'],
                muscleGroup=machine_data['muscleGroup'],
                quantity=machine_data['quantity'],
            )
            
            image = request.FILES.get('image')
            
            if image:
                img = Image.open(image)
                img_bytes_io = BytesIO()
                img.save(img_bytes_io, format='JPEG')
                new_machine.image = img_bytes_io.getvalue()

            new_machine.save()
            
            return JsonResponse({'message': 'Máquina creada', 'id': new_machine.id}, status=201)
        except ValueError as e:
            return JsonResponse({'message': 'Error al analizar los datos JSON: {}'.format(e)}, status=400)
    return JsonResponse({'message': 'Método no permitido'}, status=405)


# Vista para obtener detalles de una máquina (operación de lectura)
def machine_detail(request, machine_id):
    try:
        machine = Machines.objects.get(pk=machine_id)
    except Machines.DoesNotExist:
        return JsonResponse({'message': 'Máquina no encontrada'}, status=404)

    if request.method == 'GET':
        image_data = None

        if machine.image:
            image_data = base64.b64encode(machine.image).decode('utf-8')
            
        data = {
                'id': machine.id,
                'name': machine.name,
                'description': machine.description,
                'muscleGroup': machine.muscleGroup,
                'quantity': machine.quantity,
                'image': f"data:image/jpeg;base64,{image_data}" if image_data else None
            }
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
                        
            image = request.FILES.get('image')
        
            if image:
                machine.image = base64.b64encode(image.read()).decode('utf-8')
            else:
                machine.image = ""

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
@csrf_exempt
def delete_machine(request, machine_id):
    try:
        machine = Machines.objects.get(pk=machine_id)
    except Machines.DoesNotExist:
        return JsonResponse({'message': 'Máquina no encontrada'}, status=404)

    if request.method == 'DELETE':
        machine.delete()
        return JsonResponse({'message': 'Máquina eliminada'})
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)
