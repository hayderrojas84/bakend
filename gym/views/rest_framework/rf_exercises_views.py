import json

from PIL import Image
from io import BytesIO
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.http import Http404
from django.db.models import Count, Q


from gym.models import Exercises, Machines, ExerciseMachines
from gym.serializers import ExerciseSerializer, ExcersiseCreateSerializer
from gym.utils.pagination_utils import CustomPageNumberPagination, OrderEnum


class ExerciseListView(generics.ListAPIView):
    queryset = Exercises.objects.all()
    serializer_class = ExerciseSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        muscleGroup = self.request.query_params.get('muscleGroup', '')
        if muscleGroup:
            queryset = queryset.filter(Q(muscleGroup=muscleGroup))

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ExerciseListPaginatedView(generics.ListAPIView):
    queryset = Exercises.objects.all()
    serializer_class = ExerciseSerializer
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('perPage', openapi.IN_QUERY, description="Cantidad de items por página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sort', openapi.IN_QUERY, description="Campo por el cual ordenar", type=openapi.TYPE_STRING),
            openapi.Parameter('order', openapi.IN_QUERY, description="Orden ascendente ('asc') o descendente ('desc')", type=openapi.TYPE_STRING, enum=list(OrderEnum), default=OrderEnum.ASC),
            openapi.Parameter('search', openapi.IN_QUERY, description="Búsqueda por nombre o grupo muscular", type=openapi.TYPE_STRING),

        ],
        responses={status.HTTP_200_OK: ExerciseSerializer(many=True)}
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

class ExerciseDetailView(generics.RetrieveAPIView):
    queryset = Exercises.objects.all()
    serializer_class = ExerciseSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ExerciseCreateView(generics.CreateAPIView):
    serializer_class = ExcersiseCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        exercise_data = json.loads(request.data.get('exercise', {}))
        machines_ids = json.loads(request.data.get('machines', []))
        image = request.FILES.get('image', None)
        
        serializer = ExerciseSerializer(data=exercise_data)
        serializer.is_valid(raise_exception=True)

        exercise = serializer.save()

        if image:
            img = Image.open(image)
            img_bytes_io = BytesIO()
            img = img.convert('RGB')
            img.save(img_bytes_io, format='JPEG')
            exercise.image = img_bytes_io.getvalue()
            exercise.save()

        for machine_id in machines_ids:
            try:
                machine = Machines.objects.get(pk=machine_id)
                ExerciseMachines.objects.get_or_create(exerciseId=exercise, machineId=machine)
            except Machines.DoesNotExist:
                return Response({'message': f'Máquina con ID {machine_id} no encontrada'}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Ejercicio creado', 'id': exercise.id}, status=status.HTTP_201_CREATED, headers=headers)
    
class ExerciseUpdateView(generics.UpdateAPIView):
    serializer_class = ExerciseSerializer
    parser_classes = [MultiPartParser, FormParser]
    queryset = Exercises.objects.all()

    def update(self, request, *args, **kwargs):
        exercise = self.get_object()

        exercise_data = json.loads(request.data.get('exercise', {}))
        machines_ids = json.loads(request.data.get('machines', []))
        image = request.FILES.get('image', None)

        serializer = self.get_serializer(exercise, data=exercise_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if image:
            img = Image.open(image)
            img_bytes_io = BytesIO()
            img = img.convert('RGB')
            img.save(img_bytes_io, format='JPEG')
            exercise.image = img_bytes_io.getvalue()
            exercise.save()

        ExerciseMachines.objects.filter(exerciseId=exercise).delete()
        for machine_id in machines_ids:
            try:
                machine = Machines.objects.get(pk=machine_id)
                ExerciseMachines.objects.get_or_create(exerciseId=exercise, machineId=machine)
            except Machines.DoesNotExist:
                return Response({'message': f'Máquina con ID {machine_id} no encontrada'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Ejercicio actualizado', 'id': exercise.id}, status=status.HTTP_200_OK)

class ExerciseDeleteView(generics.DestroyAPIView):
    queryset = Exercises.objects.all()
    serializer_class = ExerciseSerializer

    def destroy(self, request, *args, **kwargs):
        exercise = self.get_object()
        exercise.delete()
        return Response({'message': 'Ejercicio eliminado'}, status=status.HTTP_204_NO_CONTENT)