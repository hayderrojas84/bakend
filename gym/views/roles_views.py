from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from gym.models import Roles
import json

# Vista para listar todos los roles (operación de lectura)
def roles_list(request):
    if request.method == 'GET':
        roles = Roles.objects.all()
        data = [model_to_dict(role) for role in roles]
        return JsonResponse(data, safe=False)
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear un nuevo rol (operación de creación)
@csrf_exempt
def create_role(request):
    if request.method == 'POST':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            role_data = json.loads(request_body)

            # Crear un nuevo rol a partir de los datos
            new_role = Roles(
                name=role_data['name'],
                description=role_data.get('description', None)
            )

            new_role.save()

            return JsonResponse({'message': 'Rol creado'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)

    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para obtener detalles de un rol (operación de lectura)
def role_detail(request, role_id):
    try:
        role = Roles.objects.get(pk=role_id)
    except Roles.DoesNotExist:
        return JsonResponse({'message': 'Rol no encontrado'}, status=404)

    if request.method == 'GET':
        data = model_to_dict(role)
        return JsonResponse(data)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para actualizar un rol (operación de actualización)
@csrf_exempt
def update_role(request, role_id):
    try:
        role = Roles.objects.get(pk=role_id)
    except Roles.DoesNotExist:
        return JsonResponse({'message': 'Rol no encontrado'}, status=404)

    if request.method == 'PUT':
        # Obtener el cuerpo de la solicitud en forma de cadena JSON
        request_body = request.body.decode('utf-8')

        try:
            # Analizar el JSON en un diccionario
            role_data = json.loads(request_body)

            # Actualizar los campos del rol con los datos proporcionados
            if 'name' in role_data:
                role.name = role_data['name']
            if 'description' in role_data:
                role.description = role_data.get('description', None)

            role.save()

            return JsonResponse({'message': 'Rol actualizado'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
        except Roles.DoesNotExist:
            return JsonResponse({'message': 'Rol no encontrado'}, status=404)
        except KeyError:
            return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para eliminar un rol (operación de eliminación)
def delete_role(request, role_id):
    try:
        role = Roles.objects.get(pk=role_id)
    except Roles.DoesNotExist:
        return JsonResponse({'message': 'Rol no encontrado'}, status=404)

    if request.method == 'DELETE':
        role.delete()
        return JsonResponse({'message': 'Rol eliminado'})
  
    return JsonResponse({'message': 'Método no permitido'}, status=405)
