#!/usr/bin/env python3

from django.shortcuts import render, render_to_response
from datetime import date
import calendar

from dashboards.ops import manager
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
