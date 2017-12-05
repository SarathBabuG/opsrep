from rest_framework import viewsets
from dashboards.models import ProductStats

from .serializers import ProductStatsSerializer

# Create your views here.
class ProductStatsViewSet(viewsets.ModelViewSet):
    queryset = ProductStats.objects.all()
    serializer_class = ProductStatsSerializer
