import json
import hashlib
import base64

from datetime import datetime, timezone
from PIL import Image
from io import BytesIO
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from gym.utils.pagination_utils import CustomPageNumberPagination, OrderEnum, PaymentEnum
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count, Q
from django.http import Http404

from gym.models import Users, People, Roles
from gym.serializers import UserSerializer, PeopleSerializer, UserCreationSerializer, UserRoleSerializer

from django.forms.models import model_to_dict


class UsersListView(generics.ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UsersListPaginatedView(generics.ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('perPage', openapi.IN_QUERY, description="Cantidad de items por página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sort', openapi.IN_QUERY, description="Campo por el cual ordenar", type=openapi.TYPE_STRING),
            openapi.Parameter('order', openapi.IN_QUERY, description="Orden ascendente ('asc') o descendente ('desc')", type=openapi.TYPE_STRING, enum=list(OrderEnum), default=OrderEnum.ASC),
            openapi.Parameter('search', openapi.IN_QUERY, description="Búsqueda por nombres, apellidos, identificación o nombre de usuario", type=openapi.TYPE_STRING),
            openapi.Parameter('paymentStatus', openapi.IN_QUERY, description="Estado del pago (Pagado o Pendiente)", type=openapi.TYPE_STRING, enum=list(PaymentEnum)),

        ],
        responses={status.HTTP_200_OK: UserSerializer(many=True)}
    )

    def get(self, request, *args, **kwargs):
        page = self.request.query_params.get('page', 1)
        per_page = self.request.query_params.get('perPage', 10)
        sort_by = self.request.query_params.get('sort', 'id')
        order = self.request.query_params.get('order', 'asc')
        search_query = self.request.query_params.get('search', '')
        payment_status = self.request.query_params.get('paymentStatus', '')

        try:
            page = int(page)
            per_page = int(per_page)
        except ValueError:
            return Response({"error": "Los parámetros 'page' y 'perPage' deben ser enteros"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        
        if order.lower() not in ['asc', 'desc']:
            return Response({"error": "El parámetro 'order' debe ser 'asc' o 'desc'"}, status=status.HTTP_400_BAD_REQUEST)

        if '.' in sort_by:
            parts = sort_by.split('.')
            if parts[0] == 'people':
                sort_by = f"people__{parts[1]}"

        if order.lower() == 'desc':
            sort_by = '-' + sort_by

        queryset = queryset.order_by(sort_by)
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(people__identification__icontains=search_query) |
                Q(people__names__icontains=search_query) |
                Q(people__lastnames__icontains=search_query)
            )
        
        queryset = queryset.annotate(
            pending_transactions=Count('people__transactions', filter=Q(people__transactions__endDate__gte=datetime.now(timezone.utc).date()))
        )
        if payment_status:
            if payment_status == 'Pendiente':
                queryset = queryset.filter(pending_transactions=0)
            elif payment_status == 'Pagado':
                queryset = queryset.filter(pending_transactions__gt=0)

        self.pagination_class.page_size = per_page
        queryset = self.filter_queryset(queryset)
        page_data = self.paginate_queryset(queryset)

        if page and not page_data:
            raise Http404("No se encontró la página")

        serializer = self.get_serializer(page_data, many=True)

        response_data = {
            'total': queryset.aggregate(total=Count('id'))['total'],
            'page': page,
            'perPage': per_page,
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class UserDetailView(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreationSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        people_data = json.loads(request.data.get('people', {}))

        existing_people = People.objects.filter(identification=people_data['identification']).first()
        if existing_people:
            return Response({'identification': ['Ya existe una persona con esta identificación']}, status=status.HTTP_400_BAD_REQUEST)
        
        user_data = json.loads(request.data.get('user', {}))
        image = request.FILES.get('image', None)

        if not user_data.get('username'):
            user_data['username'] = people_data['identification']

        if user_data.get('password'):
            password = user_data['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user_data['password'] = hashed_password
            search = 'admin'
        else:
            search = 'cliente'

        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)

        people_serializer = PeopleSerializer(data=people_data)
        people_serializer.is_valid(raise_exception=True)

        user = serializer.save()

        people_data['userId'] = user.id
        people_serializer = PeopleSerializer(data=people_data)
        people_serializer.is_valid(raise_exception=True)
        people = people_serializer.save()

        if image:
            img = Image.open(image)
            img_bytes_io = BytesIO()
            img = img.convert('RGB')
            img.save(img_bytes_io, format='JPEG')
            people.image = img_bytes_io.getvalue()
            people.save()
        
        role, created = Roles.objects.get_or_create(name=search)
        user_roles_serializer = UserRoleSerializer(data={'userId': user.id, 'roleId': role.id})
        user_roles_serializer.is_valid(raise_exception=True)
        user_roles_serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Usuario creado', 'id': user.id}, status=status.HTTP_201_CREATED, headers=headers)

class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser]
    queryset = Users.objects.all()

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        user_data = json.loads(request.data.get('user', {}))
        image = request.FILES.get('image', None)

        if 'password' in user_data:
            del user_data['password']

        serializer = self.get_serializer(user, data=user_data, partial=True)
        serializer.is_valid(raise_exception=True)

        people_data = json.loads(request.data.get('people', {}))
        people = People.objects.filter(identification=people_data['identification']).first()
        people_data['userId'] = user.id
        people_serializer = PeopleSerializer(people, data=people_data, partial=True)
        people_serializer.is_valid(raise_exception=True)

        people = people_serializer.save()

        if image:
            img = Image.open(image)
            img_bytes_io = BytesIO()
            img = img.convert('RGB')
            img.save(img_bytes_io, format='JPEG')
            people.image = img_bytes_io.getvalue()
            people.save()
        
        return Response({'message': 'Usuario actualizado', 'id': user.id}, status=status.HTTP_200_OK)

class UserDeleteView(generics.DestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({'message': 'Usuario eliminado'}, status=status.HTTP_204_NO_CONTENT)