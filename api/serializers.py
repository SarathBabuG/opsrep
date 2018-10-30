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
from rest_framework import serializers
from dashboards.models import ProductStats

class StatsSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='source.name')
    year = serializers.IntegerField(source='period.year')
    month = serializers.IntegerField(source='period.month')

    class Meta:
        model = ProductStats
        fields = ('source', 'year', 'month', 'active', 'inactive')