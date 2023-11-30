import json

from rest_framework import generics, status
from rest_framework.response import Response

from django.db.models import Q, Case, When, Value, CharField

from gym.serializers import RoutineScheduleSerializer
from gym.models import RoutineSchedules

class RoutineSchedulesListView(generics.ListAPIView):
    queryset = RoutineSchedules.objects.all()
    serializer_class = RoutineScheduleSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        peopleId = self.request.query_params.get('peopleId', '')

        if peopleId:
            queryset = queryset.filter(Q(peopleId=peopleId))
        
        order_by = Case(
            When(dayOfWeek='Lunes', then=Value(1)),
            When(dayOfWeek='Martes', then=Value(2)),
            When(dayOfWeek='Miércoles', then=Value(3)),
            When(dayOfWeek='Jueves', then=Value(4)),
            When(dayOfWeek='Viernes', then=Value(5)),
            When(dayOfWeek='Sábado', then=Value(6)),
            When(dayOfWeek='Domingo', then=Value(7)),
            default=Value(8),
            output_field=CharField(),
        )

        # Aplica el order_by después de cualquier filtro
        queryset = queryset.order_by(order_by)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoutineSchedulesByPeopleIdView(generics.ListAPIView):
    serializer_class = RoutineScheduleSerializer
    
    def get_queryset(self):
        people_id = self.kwargs['people_id']
        return RoutineSchedules.objects.filter(peopleId=people_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoutineScheduleDetailView(generics.RetrieveAPIView):
    queryset = RoutineSchedules.objects.all()
    serializer_class = RoutineScheduleSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoutineScheduleCreateView(generics.CreateAPIView):
    queryset = RoutineSchedules.objects.all()
    serializer_class = RoutineScheduleSerializer

    def create(self, request, *args, **kwargs):
        routine_schedule_data = request.data
        queryset=self.get_queryset()
        routine_day = routine_schedule_data.get('dayOfWeek', None)
        if routine_day:
            routine_schedule_same_day = queryset.filter(dayOfWeek=routine_day).first()
            if routine_schedule_same_day:
                routine_schedule_same_day.delete()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        routineSchedule = serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Horario de rutina creado', 'id': routineSchedule.id}, status=status.HTTP_201_CREATED, headers=headers)
    
class RoutineScheduleUpdateView(generics.UpdateAPIView):
    serializer_class = RoutineScheduleSerializer
    queryset = RoutineSchedules.objects.all()

    def update(self, request, *args, **kwargs):
        routineSchedule = self.get_object()

        serializer = self.get_serializer(routineSchedule, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Horario de rutina actualizado', 'id': routineSchedule.id}, status=status.HTTP_200_OK)

class RoutineScheduleDeleteView(generics.DestroyAPIView):
    queryset = RoutineSchedules.objects.all()
    serializer_class = RoutineScheduleSerializer

    def destroy(self, request, *args, **kwargs):
        routineSchedule = self.get_object()
        routineSchedule.delete()
        return Response({'message': 'Horario de rutina eliminado'}, status=status.HTTP_204_NO_CONTENT)