from rest_framework import generics, status
from rest_framework.response import Response

from gym.utils.pagination_utils import CustomPageNumberPagination, OrderEnum
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count, Q
from django.http import Http404

from gym.models import Maintenances
from gym.serializers import MaintenanceSerializer

class MaintenancesListView(generics.ListAPIView):
    queryset = Maintenances.objects.all()
    serializer_class = MaintenanceSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MaintenancesListPaginatedView(generics.ListAPIView):
    queryset = Maintenances.objects.all()
    serializer_class = MaintenanceSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        machineId = self.request.query_params.get('machineId', '')
        if machineId:
            return Maintenances.objects.filter(machineId=machineId)
        else:
            return Maintenances.objects.all()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('perPage', openapi.IN_QUERY, description="Cantidad de items por página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sort', openapi.IN_QUERY, description="Campo por el cual ordenar", type=openapi.TYPE_STRING),
            openapi.Parameter('order', openapi.IN_QUERY, description="Orden ascendente ('asc') o descendente ('desc')", type=openapi.TYPE_STRING, enum=list(OrderEnum), default=OrderEnum.ASC),
            openapi.Parameter('search', openapi.IN_QUERY, description="Búsqueda por fecha de finalización", type=openapi.TYPE_STRING)
        ],
        responses={status.HTTP_200_OK: MaintenanceSerializer(many=True)}
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
                Q(endDate__icontains=search_query)
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
    
class MaintenanceDetailView(generics.RetrieveAPIView):
    queryset = Maintenances.objects.all()
    serializer_class = MaintenanceSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MaintenanceCreateView(generics.CreateAPIView):
    serializer_class = MaintenanceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        maintenance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Mantenimiento creado', 'id': maintenance.id}, status=status.HTTP_201_CREATED, headers=headers)
