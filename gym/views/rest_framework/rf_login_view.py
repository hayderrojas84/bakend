import jwt
import hashlib
import base64


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from datetime import datetime, timedelta

from gym.models import Users, People
from gym.serializers import UserSerializer
from django.forms.models import model_to_dict

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Contraseña'),
            },
        ),
        responses={200: 'OK'},
    )
    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({'error': 'Credenciales incompletas'}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data['username']
        password = request.data['password']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            local_user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if hashed_password == local_user.password:
            
            local_people = People.objects.get(userId=local_user.id)
            payload = {
                'username': username,
                'people': model_to_dict(local_people),
                'exp': datetime.utcnow() + timedelta(hours=1)
            }

            secret_key = 'your_secret_key'
            token = jwt.encode(payload, secret_key, algorithm='HS256')

            user_data = UserSerializer(local_user).data

            image_data = None
            if local_people.image:
                image_data = base64.b64encode(local_people.image).decode('utf-8')
                user_data['people']['image'] = f"data:image/jpeg;base64,{image_data}" if image_data else None

            return Response({
                'token': token,
                'user': user_data
            })
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
