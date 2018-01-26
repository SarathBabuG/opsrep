from rest_framework import viewsets
from rest_framework.response import Response
from dashboards.models import Stats
from dashboards.ops import properties

from .serializers import StatsSerializer


class StatsViewSet(viewsets.ModelViewSet):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer


class CNStatsViewSet(viewsets.ViewSet):

    def list(self, request, format=None):
        return Response(properties.statsObj)
