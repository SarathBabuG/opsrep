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
from dashboards.models import Stats

class StatsSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name')
    source = serializers.CharField(source='source.name')
    year = serializers.IntegerField(source='period.year')
    month = serializers.IntegerField(source='period.month')

    class Meta:
        model = Stats
        fields = ('product', 'source', 'year', 'month', 'active', 'inactive')