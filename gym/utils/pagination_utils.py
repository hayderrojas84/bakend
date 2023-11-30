from rest_framework.pagination import PageNumberPagination
from enum import Enum

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'perPage'

class OrderEnum(Enum):
    ASC = 'asc'
    DESC = 'desc'

class PaymentEnum(Enum):
    PAGADO = 'Pagado'
    PENDIENTE = 'Pendiente'