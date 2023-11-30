import json
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework import generics
from PIL import Image
from io import BytesIO
from gym.utils.pagination_utils import CustomPageNumberPagination, OrderEnum
from gym.serializers import MachineSerializer
from gym.models import Machines
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import Http404
from django.db.models import Count, Q


class MachinesListView(generics.ListAPIView):
    queryset = Machines.objects.all()
    serializer_class = MachineSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        muscleGroup = self.request.query_params.get('muscleGroup', '')
        if muscleGroup:
            queryset = queryset.filter(Q(muscleGroup=muscleGroup))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MachinesListPaginatedView(generics.ListAPIView):
    queryset = Machines.objects.all()
    serializer_class = MachineSerializer
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('perPage', openapi.IN_QUERY, description="Cantidad de items por página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sort', openapi.IN_QUERY, description="Campo por el cual ordenar", type=openapi.TYPE_STRING),
            openapi.Parameter('order', openapi.IN_QUERY, description="Orden ascendente ('asc') o descendente ('desc')", type=openapi.TYPE_STRING, enum=list(OrderEnum), default=OrderEnum.ASC),
            openapi.Parameter('search', openapi.IN_QUERY, description="Búsqueda por nombre o grupo muscular", type=openapi.TYPE_STRING),

        ],
        responses={status.HTTP_200_OK: MachineSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        page = self.request.query_params.get('page', 1)
        per_page = self.request.query_params.get('perPage', 10)
        sort_by = self.request.query_params.get('sort', 'id')
        order = self.request.query_params.get('order', 'asc')
        search_query = self.request.query_params.get('search', '')

        try:
            page = int(page)
            per_page = int(per_page)
        except ValueError:
            return Response({"error": "Los parámetros 'page' y 'perPage' deben ser enteros"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()

        if order.lower() not in ['asc', 'desc']:
            return Response({"error": "El parámetro 'order' debe ser 'asc' o 'desc'"}, status=status.HTTP_400_BAD_REQUEST)

        if order.lower() == 'desc':
            sort_by = '-' + sort_by
        
        queryset = queryset.order_by(sort_by)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(muscleGroup__icontains=search_query)
            )
        
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

class MachineDetailView(generics.RetrieveAPIView):
    queryset = Machines.objects.all()
    serializer_class = MachineSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MachineCreateView(generics.CreateAPIView):
    serializer_class = MachineSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        machine_data = json.loads(request.data.get('machine', {}))
        image = request.FILES.get('image', None)
        
        serializer = self.get_serializer(data=machine_data)
        serializer.is_valid(raise_exception=True)

        machine = serializer.save()

        if image:
            img = Image.open(image)
            img_bytes_io = BytesIO()
            img = img.convert('RGB')
            img.save(img_bytes_io, format='JPEG')
            machine.image = img_bytes_io.getvalue()
            machine.save()

        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Máquina creada', 'id': machine.id}, status=status.HTTP_201_CREATED, headers=headers)
    
class MachineUpdateView(generics.UpdateAPIView):
    serializer_class = MachineSerializer
    parser_classes = [MultiPartParser, FormParser]
    queryset = Machines.objects.all()

    def update(self, request, *args, **kwargs):
        machine = self.get_object()

        machine_data = json.loads(request.data.get('machine', {}))
        image = request.FILES.get('image', None)

        serializer = self.get_serializer(machine, data=machine_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if image:
            img = Image.open(image)
            img_bytes_io = BytesIO()
            img = img.convert('RGB')
            img.save(img_bytes_io, format='JPEG')
            machine.image = img_bytes_io.getvalue()
            machine.save()

        return Response({'message': 'Máquina actualizada', 'id': machine.id}, status=status.HTTP_200_OK)

class MachineDeleteView(generics.DestroyAPIView):
    queryset = Machines.objects.all()
    serializer_class = MachineSerializer

    def destroy(self, request, *args, **kwargs):
        machine = self.get_object()
        machine.delete()
        return Response({'message': 'Máquina eliminada'}, status=status.HTTP_204_NO_CONTENT)