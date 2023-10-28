from functools import wraps
from django.http import JsonResponse
from gym.middleware import AuthMiddleware

def protected_endpoint(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Llama al middleware para realizar la autenticación
        auth_middleware = AuthMiddleware(get_response=view_func)
        response = auth_middleware(request)

        # Verifica la respuesta del middleware
        if response.status_code == 401:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        # Si la autenticación es exitosa, ejecuta la vista
        return view_func(request, *args, **kwargs)

    return wrapper
