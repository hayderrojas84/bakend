import jwt
import hashlib
import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from datetime import datetime, timedelta
from gym.models import Users

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
            return JsonResponse({'token': token})
        else:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
