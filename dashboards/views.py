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
from django.shortcuts import render, render_to_response
from datetime import date
import calendar

from dashboards.ops import manager, properties
from .models import ProductStats


# Create your views here.
def main(request):
    months = dict((k, v) for k,v in enumerate(calendar.month_name))
    del months[0]
    context = manager.pod_rsrc_stats_doughnut()
    return render(request, 'main.html', context)


def dashboard(request):
    if not properties.pingdom:
        pass

    from datetime import datetime, timedelta
    summary_period = 7
    last_7dates = []
    for i in range(summary_period):
        last_7dates.append((datetime.now() - timedelta(days=(i))).strftime("%b %d"))
    last_7dates.reverse()
    return render(request, 'views/dashboard.html', {'pingdom_stats': properties.pingdom, 'last_7dates': last_7dates})


def piecharts(request):
    formdata = request.GET.dict()
    month = int(formdata.get('month', date.today().month))
    year  = int(formdata.get('year', date.today().year))
 
    months = dict((k, v) for k,v in enumerate(calendar.month_name))
    del months[0]
 
    context = manager.pod_rsrc_stats_doughnut(month, year)
 
    data = ProductStats.objects.filter(period__year=2017, period__month__gt=(12-3))
    _hash = []
    for d in data:
        _hash.append({
            'month': d.period.month,
            'source' : d.source.name,
            'active' : d.active,
            'inactive' : d.inactive,
        })
     
    context.update({'data': str(_hash) })
    context.update({'month': month, 'year': year, 'months': months, 'years': [2017, 2018, 2019]})
    return render(request, 'views/piecharts.html', context)


def charts(request):
    context = manager.pod_rsrc_stats_pie()
    return render(request, 'views/charts.html', context)

def product_stats(request):
    context = manager.pod_product_stats()
    return render(request, 'views/product_stats.html', context)

def resource_stats(request):
    context = manager.get_monthly_usage_stats()
    return render(request, 'views/resource_stats.html', context)


def page404():
    return render_to_response('views/404.html')


def cnsessions(request):
    '''
    var fData=[
        {csnode:'demo01',sessions:{agent:4786, gateway:249}}
        ,{csnode:'demo02',sessions:{agent:1101, gateway:674}}
        ,{csnode:'demo03',sessions:{agent:932, gateway:418}}
        ,{csnode:'demo04',sessions:{agent:832, gateway:1862}}
        ,{csnode:'demo05',sessions:{agent:4481, gateway:948}}
        ,{csnode:'demo06',sessions:{agent:1619, gateway:1063}}
        ,{csnode:'demo07',sessions:{agent:1819, gateway:1203}}
        ,{csnode:'demo08',sessions:{agent:4498, gateway:942}}
        ,{csnode:'demo09',sessions:{agent:797, gateway:1534}}
        ,{csnode:'demo10',sessions:{agent:162, gateway:471}}
        ];
    '''
    boards = []
    cdata  = []
    count  = 0
    _stats = properties.statsObj.get('1arc', {})
    if not _stats:
        return render_to_response('views/no_data.html')

    for cn in sorted(_stats.keys()):
        cdata.append({
            "csnode"   : cn.split("-")[0],
            "sessions" : {
                "agent"   : int(_stats[cn]["Agent"]),
                "gateway" : int(_stats[cn]["Gateway"])
            }
        })
        #count += 1
        #if count == 10:
        #    count = 0
        #    boards.append(cdata)
        #    cdata = []

    #if cdata:
    #    boards.append(cdata)

    return render(request, 'views/cnsessions.html', { "csn_sessions_data": cdata, "agents_data": properties.statsObj.get('1arc', {}) })


def elasticsearch(request):
    context = manager.get_elasticsearch_cluster_info()
    return render(request, 'views/elasticsearch.html', context)


def cassandra(request):
    return render_to_response('views/no_data.html')


def redis(request):
    return render_to_response('views/no_data.html')

