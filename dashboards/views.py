#!/usr/bin/env python3

from django.shortcuts import render, render_to_response
#from django.utils.safestring import mark_safe
#from django.utils.html import escapejs
from datetime import date
import json, calendar

from dashboards.ops import manager, properties
from .models import Stats


# Create your views here.
def main(request):
    months = dict((k, v) for k,v in enumerate(calendar.month_name))
    del months[0]
    context = manager.product_stats()
    return render(request, 'main.html', context)


def dashboard(request):
    formdata = request.GET.dict()
    month = int(formdata.get('month', date.today().month))
    year  = int(formdata.get('year', date.today().year))

    months = dict((k, v) for k,v in enumerate(calendar.month_name))
    del months[0]

    context = manager.product_stats(month, year)

    data = Stats.objects.filter(period__year=2017, period__month__gt=(12-3), product__name='ITOM')
    _hash = []
    for d in data:
        _hash.append({
            'month': d.period.month,
            'product': d.product.name,
            'source' : d.source.name,
            'active' : d.active,
            'inactive' : d.inactive,
        })
    
    context.update({'data': str(_hash) })
    
    context.update({'month': month, 'year': year, 'months': months, 'years': [2016, 2017]})
    return render(request, 'views/dashboard.html', context)


def charts(request):
    context = manager.pod_rsrc_stats()
    return render(request, 'views/charts.html', context)


def page404(request):
    return  render_to_response('views/404.html')


def cnsessions(request):
    '''
    var fData=[
        {State:'AL',freq:{agent:4786, gateway:249}}
        ,{State:'AZ',freq:{agent:1101, gateway:674}}
        ,{State:'CT',freq:{agent:932, gateway:418}}
        ,{State:'DE',freq:{agent:832, gateway:1862}}
        ,{State:'FL',freq:{agent:4481, gateway:948}}
        ,{State:'GA',freq:{agent:1619, gateway:1063}}
        ,{State:'IA',freq:{agent:1819, gateway:1203}}
        ,{State:'IL',freq:{agent:4498, gateway:942}}
        ,{State:'IN',freq:{agent:797, gateway:1534}}
        ,{State:'KS',freq:{agent:162, gateway:471}}
        ];
    '''
    cdata = []
    for cn, cn_data in properties.statsObj.get('1arc', {}).items():
        cdata.append({
            "csnode"   : cn.split("-")[0],
            "sessions" : {
                "agent"   : int(cn_data["Agent"]),
                "gateway" : int(cn_data["Gateway"])
            }
        })

    return  render(request, 'views/cnsessions.html', { "csn_sessions": cdata })
