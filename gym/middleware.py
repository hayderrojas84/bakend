# middleware.py

import jwt
from django.http import JsonResponse
from gym.models import Users

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lógica de autenticación
        auth_header = request.headers.get('Authorization')

        if auth_header:
            # Verifica si el header comienza con 'Bearer '
            if auth_header.startswith('Bearer '):
                # Si comienza con 'Bearer ', quita el prefijo 'Bearer '
                token = auth_header.split('Bearer ')[1]
            else:
                # De lo contrario, utiliza el header como está
                token = auth_header
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        try:
            # Decodifica el token JWT y obtén el payload
            decoded_token = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])

            username = decoded_token.get('username')

            # Busca el usuario en la base de datos por el nombre de usuario
            user = Users.objects.get(username=username)

            # Si el usuario es válido, establece el usuario en la solicitud
            request.user = user
        except (jwt.InvalidTokenError, Users.DoesNotExist) as e:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        return self.get_response(request)
