import json

from rest_framework import generics, status
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.http import Http404
from django.db.models import Count, Q

from gym.utils.pagination_utils import CustomPageNumberPagination, OrderEnum
from gym.serializers import RoutineSerializer
from gym.models import Routines, Exercises, RoutinesExercises

class RoutinesListView(generics.ListAPIView):
    serializer_class = RoutineSerializer
    queryset = Routines.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        muscleGroup = self.request.query_params.get('muscleGroup', '')
        goal = self.request.query_params.get('goal', '')
        difficulty = self.request.query_params.get('difficulty', '')

        if muscleGroup:
            queryset = queryset.filter(Q(muscleGroup=muscleGroup))

        if goal:
            queryset = queryset.filter(Q(goal=goal))
        
        if difficulty:
            queryset = queryset.filter(Q(difficulty=difficulty))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RoutineListPaginatedView(generics.ListAPIView):
    queryset = Routines.objects.all()
    serializer_class = RoutineSerializer
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('perPage', openapi.IN_QUERY, description="Cantidad de items por página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sort', openapi.IN_QUERY, description="Campo por el cual ordenar", type=openapi.TYPE_STRING),
            openapi.Parameter('order', openapi.IN_QUERY, description="Orden ascendente ('asc') o descendente ('desc')", type=openapi.TYPE_STRING, enum=list(OrderEnum), default=OrderEnum.ASC),
            openapi.Parameter('search', openapi.IN_QUERY, description="Búsqueda por nombre o grupo muscular", type=openapi.TYPE_STRING),

        ],
        responses={status.HTTP_200_OK: RoutineSerializer(many=True)}
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

class RoutineDetailView(generics.RetrieveAPIView):
    queryset = Routines.objects.all()
    serializer_class = RoutineSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoutineCreateView(generics.CreateAPIView):
    serializer_class = RoutineSerializer

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        routine_data = data.get('routine', {})
        exercises = data.get('exercises', [])
        
        serializer = self.get_serializer(data=routine_data)
        serializer.is_valid(raise_exception=True)

        routine = serializer.save()

        for exercise_id in exercises:
            try:
                exercise = Exercises.objects.get(pk=exercise_id)
                RoutinesExercises.objects.get_or_create(exerciseId=exercise, routineId=routine)
            except Exercises.DoesNotExist:
                return Response({'message': f'Ejercicio con ID {exercise_id} no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Rutina creada', 'id': routine.id}, status=status.HTTP_201_CREATED, headers=headers)
    
class RoutineUpdateView(generics.UpdateAPIView):
    serializer_class = RoutineSerializer
    queryset = Routines.objects.all()

    def update(self, request, *args, **kwargs):
        routine = self.get_object()

        data = json.loads(request.body)
        routine_data = data.get('routine', {})
        exercises = data.get('exercises', [])

        serializer = self.get_serializer(routine, data=routine_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()


        RoutinesExercises.objects.filter(routineId=routine).delete()
        for exercise_id in exercises:
            try:
                exercise = Exercises.objects.get(pk=exercise_id)
                RoutinesExercises.objects.get_or_create(exerciseId=exercise, routineId=routine)
            except Exercises.DoesNotExist:
                return Response({'message': f'Ejercicio con ID {exercise_id} no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Rutina actualizada', 'id': routine.id}, status=status.HTTP_200_OK)

class DeleteRoutineView(generics.DestroyAPIView):
    queryset = Routines.objects.all()
    serializer_class = RoutineSerializer

    def destroy(self, request, *args, **kwargs):
        routine = self.get_object()
        routine.delete()
        return Response({'message': 'Rutina eliminada'}, status=status.HTTP_204_NO_CONTENT)