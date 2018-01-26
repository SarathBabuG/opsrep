from rest_framework import serializers
from dashboards.models import Stats

class StatsSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name')
    source = serializers.CharField(source='source.name')
    year = serializers.IntegerField(source='period.year')
    month = serializers.IntegerField(source='period.month')

    class Meta:
        model = Stats
        fields = ('product', 'source', 'year', 'month', 'active', 'inactive')