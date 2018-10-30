'''
/*
 * This computer program is the confidential information and proprietary trade
 * secret  of  OpsRamp, Inc. Possessions and use of this program must conform
 * strictly to the license agreement between the user and OpsRamp, Inc., and
 * receipt or possession does not convey any rights to divulge, reproduce, or
 * allow others to use this program without specific written authorization of
 * OpsRamp, Inc.
 * 
 * Copyright (c) 2018 OpsRamp, Inc. All rights reserved. 
 */
'''
from rest_framework import viewsets
from rest_framework.response import Response
from dashboards.models import ProductStats
from dashboards.ops import properties

from .serializers import StatsSerializer


class StatsViewSet(viewsets.ModelViewSet):
    queryset = ProductStats.objects.all()
    serializer_class = StatsSerializer


class CNStatsViewSet(viewsets.ViewSet):

    def list(self, request, format=None):
        return Response(properties.statsObj)
