from rest_framework import viewsets
from dashboards.models import ProductStats, Stats

from .serializers import ProductStatsSerializer, StatsSerializer

# Create your views here.
class ProductStatsViewSet(viewsets.ModelViewSet):
    queryset = ProductStats.objects.all()
    serializer_class = ProductStatsSerializer

class StatsViewSet(viewsets.ModelViewSet):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer
