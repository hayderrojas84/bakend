import hashlib
import json
import base64

from datetime import datetime, date, timezone
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db import IntegrityError
from PIL import Image, UnidentifiedImageError
from io import BytesIO

from gym.models import Users, People, Roles, UserRoles, Transactions



from gym.decorators import protected_endpoint

# Vista para listar todos los usuarios (operación de lectura)
def user_list(request):
    if request.method == 'GET':
          users = Users.objects.all().values()  # Obtener los valores de la consulta en forma de diccionarios
          transactions = Transactions.objects.all().values()
          
          data = []
          for user in users:
              # Excluir el campo 'password' si existe en el diccionario del usuario
              if 'password' in user:
                  del user['password']

              del user['created']
              del user['updated']

              try:
                people = People.objects.get(userId=user['id'])
                if people:
                  people_data = model_to_dict(people)

                  image_data = None
                  if people.image:
                      image_data = base64.b64encode(people.image).decode('utf-8')

                  people_data['image'] = f"data:image/jpeg;base64,{image_data}" if image_data else None
                  user['people'] = people_data
                  
                  peopleTransactions = transactions.filter(peopleId=people.id)
                  
                  user['paymentStatus'] = 'Pendiente'
                  
                  if len(peopleTransactions):
                    currentDate = datetime.now(timezone.utc).date()
                    for transaction in peopleTransactions:
                      if transaction['endDate'] >= currentDate:
                        user['paymentStatus'] = 'Pagado'
                                    
              except People.DoesNotExist:
                  user['people']: {}
              
              data.append(user)
              
          return JsonResponse(data, safe=False)
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para crear un nuevo usuario (operación de creación)
@csrf_exempt
def create_user(request):
  if request.method == 'POST':
    
    try:
      data = {
          'user': json.loads(request.POST['user']),
          'people': json.loads(request.POST['people'])
      }

      user = data.get('user')
      people = data.get('people')
        
      # Crear un nuevo usuario a partir de los datos
      new_user = Users(
        username = user['username'] if user['username'] is not None else people['identification']
      )

      if user['password'] is not None:
        password = user['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        new_user.password = hashed_password
        search = 'admin'
      else:
        search = 'cliente'

      new_user.save()

      try:
          local_people = People.objects.get(identification=people['identification'])
          if (local_people and local_people.userId is not None):
              if (new_user.id is not None):
                new_user.delete()
              return JsonResponse({'message': 'Ya existe un usuario asociado con esta persona...'}, status=400)

      except People.DoesNotExist:
          new_people = People(
            identification=people['identification'],
            names=people['names'],
            lastnames=people['lastnames'],
            birthdate=people['birthdate'],
            email=people['email'],
            address=people['address'],
            mobile=people['mobile'],
            weight=people['weight'],
            height=people['height'],
            bloodType=people['bloodType'],
            gender=people['gender']
          )

          new_people.userId = new_user

          image = request.FILES.get('image')
                
          if image:
              img = Image.open(image)
              img_bytes_io = BytesIO()
              img = img.convert('RGB')
              img.save(img_bytes_io, format='JPEG')
              new_people.image = img_bytes_io.getvalue()
          new_people.save()

      role, created = Roles.objects.get_or_create(name=search)
      UserRoles.objects.get_or_create(userId=new_user, roleId=role)    

      return JsonResponse({'message': 'Usuario creado', 'id': new_user.id}, status=201)
    except json.JSONDecodeError:
      return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
    except KeyError:
      return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    except IntegrityError:
      return JsonResponse({'message': 'Error con la integridad de los datos'}, status=400)
    except UnidentifiedImageError:
      return JsonResponse({'message': 'Error al procesar la imagen'}, status=400)
    except Exception as e:
      if new_user.id is not None:
          new_user.delete()
      return JsonResponse({'message': 'Error inesperado al crear el usuario'}, status=500)
  return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para obtener detalles de un usuario (operación de lectura)
def user_detail(request, user_id):
  try:
    user = Users.objects.get(pk=user_id)
    people = People.objects.get(userId=user.id)
  except Users.DoesNotExist:
    return JsonResponse({'message': 'Usuario no encontrado'}, status=404)
  except People.DoesNotExist:
    return JsonResponse({'message': 'Persona no encontrada'}, status=404)

  if request.method == 'GET':
    data = model_to_dict(user)
    del data['password']

    image_data = None
    if people.image:
      image_data = base64.b64encode(people.image).decode('utf-8')
    
    peopleTransactions = Transactions.objects.filter(peopleId=people.id)
                  
    data['paymentStatus'] = 'Pendiente'
    
    if len(peopleTransactions):
      currentDate = datetime.now(timezone.utc).date()
      for transaction in peopleTransactions:
        if transaction['endDate'] >= currentDate:
          data['paymentStatus'] = 'Pagado'

    people_data = model_to_dict(people)
    people_data['image'] = f"data:image/jpeg;base64,{image_data}" if image_data else None

    data['people'] = people_data
    return JsonResponse(data)
  return JsonResponse({'message': 'Método no permitido'}, status=405)

# Vista para actualizar un usuario (operación de actualización)
@csrf_exempt
def update_user(request, user_id):
  try:
    user = Users.objects.get(pk=user_id)
  except Users.DoesNotExist:
    return JsonResponse({'message': 'Usuario no encontrado'}, status=404)

  if request.method == 'POST':
    # Obtener el cuerpo de la solicitud en forma de cadena JSON
    try:
        data = {
           'user': json.loads(request.POST['user']),
           'people': json.loads(request.POST['people'])
        }
        
        user_data = data['user']

        # Obtener el usuario que deseas actualizar
        user = Users.objects.get(pk=user_id)

        # Actualizar los campos del usuario con los datos proporcionados
        if 'username' in user_data:
            user.username = user_data['username']
        
        if 'password' in user_data:
            password = user_data['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user.password = hashed_password

        user.save()

        people_data = data['people']
        people = People.objects.get(identification=people_data['identification'])

        if 'names' in people_data:
            people.names = people_data['names']
        if 'lastnames' in people_data:
            people.lastnames = people_data['lastnames']
        if 'birthdate' in people_data:
            people.birthdate = people_data['birthdate']
        if 'email' in people_data:
            people.email = people_data['email']
        if 'address' in people_data:
            people.address = people_data['address']
        if 'mobile' in people_data:
            people.mobile = people_data['mobile']
        if 'weight' in people_data:
            people.weight = people_data['weight']
        if 'height' in people_data:
            people.height = people_data['height']
        if 'bloodType' in people_data:
            people.bloodType = people_data['bloodType']
        if 'gender' in people_data:
            people.gender = people_data['gender']

        image = request.FILES.get('image')
                
        if image:
            img = Image.open(image)
            img_bytes_io = BytesIO()
            img = img.convert('RGB')
            img.save(img_bytes_io, format='JPEG')
            people.image = img_bytes_io.getvalue()

        people.save()

        return JsonResponse({'message': 'Usuario actualizado'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Error al analizar los datos JSON'}, status=400)
    except Users.DoesNotExist:
        return JsonResponse({'message': 'Usuario no encontrado'}, status=404)
    except KeyError:
        return JsonResponse({'message': 'Faltan campos requeridos en los datos JSON'}, status=400)
    
  return JsonResponse({'message': 'Método no permitido, prueba con un POST'}, status=405)

# Vista para eliminar un usuario (operación de eliminación)
@csrf_exempt
def delete_user(request, user_id):
  try:
    user = Users.objects.get(pk=user_id)
  except Users.DoesNotExist:
    return JsonResponse({'message': 'Usuario no encontrado'}, status=404)

  if request.method == 'DELETE':
    user.delete()
    return JsonResponse({'message': 'Usuario eliminado'})
  
  return JsonResponse({'message': 'Método no permitido'}, status=405)
