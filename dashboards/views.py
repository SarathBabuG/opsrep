#!/usr/bin/env python3

from django.shortcuts import render #, render_to_response
from datetime import date
import calendar

from dashboards.ops import manager
from .models import Stats

colors_codes = {
    'green'       : '#008000',
    'olive'       : '#6B8E23',
    'limegreen'   : '#32CD32',
    'yellowgreen' : '#9ACD32',

    'red'         : '#D55454',
    'crimson'     : '#DC143C',
    'salmon'      : '#FA8072',
    'indianred'   : '#CD5C5C',
    'lightcoral'  : '#F08080',
    'tomato'      : '#FF6347',
    
    'blue'          : '#36A2EB',
    'navy'          : '#000080',
    'royalblue'     : '#4169E1',
    'slateblue'     : '#6A5ACD',
    'darkslateblue' : '#483D8B',
    'steelblue'     : '#4682B4',
    'cornflowerblue': '#6495ED',
    
    'yellow'      : '#FFCE56'

}


# Create your views here.
def main(request):
    months = dict((k, v) for k,v in enumerate(calendar.month_name))
    del months[0]
    context = manager.product_stats()
    return render(request, 'main.html', context)


def charts(request):
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
    return render(request, 'views/charts.html', context)



def charts2(request):
    context = manager.pstats()
    return render(request, 'views/charts2.html', context)

