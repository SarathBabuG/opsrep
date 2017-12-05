from rest_framework import serializers, viewsets
from .models import ProductStats

class ProductStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStats
        fields = ('year', 'month', 'product', 'class_code', 'class_state', 'count')

class ProductStatsViewSet(viewsets.ModelViewSet):
    queryset = ProductStats.objects.all()
    serializer_class = ProductStatsSerializer