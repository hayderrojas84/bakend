from functools import wraps
from django.http import JsonResponse
from gym.middleware import AuthMiddleware

def protected_function_endpoint(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_middleware = AuthMiddleware(get_response=view_func)
        response = auth_middleware(request)

        if response.status_code == 401:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper

def protected_class_endpoint(class_view):
    class WrappedView(class_view):
        def dispatch(self, request, *args, **kwargs):
            auth_middleware = AuthMiddleware(get_response=super().dispatch)
            response = auth_middleware(request)

            if response.status_code == 401:
                return JsonResponse({'error': 'Unauthorized'}, status=401)
            
            return super().dispatch(request, *args, **kwargs)

    return WrappedView

