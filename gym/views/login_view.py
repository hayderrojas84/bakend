import jwt
import hashlib
import json
import base64

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.forms.models import model_to_dict
from datetime import datetime, timedelta
from gym.models import Users, People

@csrf_exempt
def login(request):
    if request.method == 'POST':

        request_body = request.body.decode('utf-8')

        credentials = json.loads(request_body)

        username = credentials['username']
        password = credentials['password']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Autenticación del usuario
        try:
            localUser = Users.objects.get(username=username)
            localPeople = People.objects.get(userId=localUser.id)
        except Users.DoesNotExist:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
        
        if hashed_password == localUser.password:
            # Generar token JWT
            payload = {
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=1)
            }

            secret_key = 'your_secret_key'  # Reemplaza con tu propia clave secreta
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            user_dict = model_to_dict(localUser)
            
            people_dict = model_to_dict(localPeople)
            
            
            image_data = None
            if localPeople.image:
              print('image')
              image_data = base64.b64encode(localPeople.image).decode('utf-8')
              people_dict['image'] = f"data:image/jpeg;base64,{image_data}" if image_data else None
            
            user_dict['people'] = people_dict if people_dict else None
            
            del user_dict['password']
            
            return JsonResponse({
                'token': token,
                'user': user_dict
            })
        else:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
