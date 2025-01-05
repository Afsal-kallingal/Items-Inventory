
from rest_framework import viewsets
from apps.main.pagination import CustomPagination

class BaseModelViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
