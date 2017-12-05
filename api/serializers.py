from rest_framework import serializers
from dashboards.models import ProductStats

class ProductStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStats
        fields = ('product', 'class_code', 'class_state', 'count', 'month', 'year')
