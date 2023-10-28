import hashlib
import json

from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from gym.models import Users, Roles, UserRoles

from gym.decorators import protected_endpoint

# Vista para listar todos los usuarios (operación de lectura)
@protected_endpoint
def user_list(request):
    if request.method == 'GET':
          users = Users.objects.all().values()  # Obtener los valores de la consulta en forma de diccionarios
          data = []
          for user in users:
              # Excluir el campo 'password' si existe en el diccionario del usuario
              if 'password' in user:
                  del user['password']
              data.append(user)
          return JsonResponse(data, safe=False)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear un nuevo usuario (operación de creación)
@csrf_exempt
def create_user(request):
  if request.method == 'POST':
    # Obtener el cuerpo de la solicitud en forma de cadena JSON
    request_body = request.body.decode('utf-8')

    try:
      # Analizar el JSON en un diccionario
      user_data = json.loads(request_body)

      # Crear un nuevo usuario a partir de los datos
      new_user = Users(
        username=user_data['username'],
        identification=user_data['identification'],
        names=user_data['names'],
        lastnames=user_data['lastnames'],
        birthdate=user_data['birthdate'],
        email=user_data['email'],
        address=user_data['address'],
        weight=user_data['weight'],
        height=user_data['height'],
        bloodType=user_data['bloodType'],
        gender=user_data['gender']
      )

      if 'password' in user_data:
        password = user_data['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        new_user.password = hashed_password
        search = 'admin'
      else:
        search = 'cliente'

      new_user.save()
      role, created = Roles.objects.get_or_create(name=search)
      UserRoles.objects.get_or_create(userId=new_user, roleId=role)    

      return JsonResponse({'message': 'Usuario creado'}, status=201)
    except json.JSONDecodeError:
      return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
    except KeyError:
      return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)

  return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para obtener detalles de un usuario (operación de lectura)
def user_detail(request, user_id):
  try:
    user = Users.objects.get(pk=user_id)
  except Users.DoesNotExist:
    return JsonResponse({'message': 'Usuario no encontrado'}, status=404)

  if request.method == 'GET':
    data = model_to_dict(user)
    return JsonResponse(data)
  return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para actualizar un usuario (operación de actualización)
@csrf_exempt
def update_user(request, user_id):
  try:
    user = Users.objects.get(pk=user_id)
  except Users.DoesNotExist:
    return JsonResponse({'message': 'Usuario no encontrado'}, status=404)

  if request.method == 'PUT':
    # Obtener el cuerpo de la solicitud en forma de cadena JSON
    request_body = request.body.decode('utf-8')

    try:
        # Analizar el JSON en un diccionario
        user_data = json.loads(request_body)

        # Obtener el usuario que deseas actualizar
        user = Users.objects.get(pk=user_id)

        # Actualizar los campos del usuario con los datos proporcionados
        if 'username' in user_data:
            user.username = user_data['username']
        if 'identification' in user_data:
            user.identification = user_data['identification']
        if 'names' in user_data:
            user.names = user_data['names']
        if 'lastnames' in user_data:
            user.lastnames = user_data['lastnames']
        if 'birthdate' in user_data:
            user.birthdate = user_data['birthdate']
        if 'email' in user_data:
            user.email = user_data['email']
        if 'address' in user_data:
            user.address = user_data['address']
        if 'weight' in user_data:
            user.weight = user_data['weight']
        if 'height' in user_data:
            user.height = user_data['height']
        if 'bloodType' in user_data:
            user.bloodType = user_data['bloodType']
        if 'gender' in user_data:
            user.gender = user_data['gender']
        
        if 'password' in user_data:
            password = user_data['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user.password = hashed_password

        user.save()

        return JsonResponse({'message': 'Usuario actualizado'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
    except Users.DoesNotExist:
        return JsonResponse({'message': 'Usuario no encontrado'}, status=404)
    except KeyError:
        return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    
  return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para eliminar un usuario (operación de eliminación)
def delete_user(request, user_id):
  try:
    user = Users.objects.get(pk=user_id)
  except Users.DoesNotExist:
    return JsonResponse({'message': 'Usuario no encontrado'}, status=404)

  if request.method == 'DELETE':
    user.delete()
    return JsonResponse({'message': 'Usuario eliminado'})
  
  return JsonResponse({'message': 'Método no permitido'}, status=405)
