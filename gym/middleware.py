import jwt
from django.http import JsonResponse
from gym.models import Users

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')

        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split('Bearer ')[1]
            else:
                token = auth_header
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        try:
            decoded_token = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])

            username = decoded_token.get('username')

            try:
                user = Users.objects.get(username=username)
                if hasattr(user, 'is_active') and not user.is_active:
                    return JsonResponse({'error': 'Unauthorized'}, status=401)
                request.user = user
            except Users.DoesNotExist:
                return JsonResponse({'error': 'Unauthorized'}, status=401)

        except jwt.InvalidTokenError as e:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        return self.get_response(request)
