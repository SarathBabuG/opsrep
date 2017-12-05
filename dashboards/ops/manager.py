from datetime import date
import json, calendar

from dashboards.models import ProductStats, Stats, Period


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


def product_stats(month=date.today().month, year=date.today().year):
    '''
    allstats = ProductStats.objects.all()
    active = stats.filter(month=date.today().month, year=date.today().year, product='itom', class_state=1).values('class_code','count')
    deactive = stats.filter(month=date.today().month, year=date.today().year, product='itom', class_state=0).values('class_code','count')
    '''

    stats = ProductStats.objects.filter(month=month, year=year).order_by('product')
    states = {0: 'Active', 1: 'Inactive'}
    data = {}
    for stat in stats:
        if stat.product not in data:
            data[stat.product] = {}

        if stat.class_code not in data[stat.product]:
            data[stat.product][stat.class_code] = {}

        try:
            data[stat.product][stat.class_code].update({states[stat.class_state]: stat.count})
        except:
            data[stat.product][stat.class_code] = {states[stat.class_state]: stat.count}

    chart_type = "doughnut"
    options    = {"responsive": True}
    labels     = ['Active', 'Inactive']
    datasets   = []
    
    for product, product_data in data.items():
        for class_code, class_data in product_data.items():
            dashboard = product + ' - ' + class_code
            colors    = [colors_codes['olive'], colors_codes['red']]
            values    = [class_data['Active'], class_data['Inactive']]
            datasets.append({
                'name': dashboard,
                'dataset': {
                    'label': dashboard,
                    'data': values,
                    'backgroundColor': colors,
                    'hoverBackgroundColor': colors
                }
            })
    
    context = {'chart_type': chart_type, 'options': str(json.dumps(options)), 'labels': str(json.dumps(labels)), 'data_sets': str(json.dumps(datasets)), 'dsets': datasets}
    return context



def pod_rsrc_stats():
    last = 3

    months = dict((k, v) for k,v in enumerate(calendar.month_name))
    del months[0]
    
    month = date.today().month
    year  = date.today().year

    sources    = ['msp', 'tenants', 'users']
    chart_type = "bar"
    options    = {"responsive": True}
    datasets   = []
    products = ['ITOM', 'IMONSITE']

    for product in products:
        itom_stats = Stats.objects.filter(period__year=year, period__month__gt=(month-last), period__month__lt=(month+1), product__name=product).order_by('period__month')
    
        product_hash = {}
        distinct_months = set()
        for _stat in itom_stats:
            distinct_months.add(_stat.period.month)
            if _stat.source.name not in product_hash:
                product_hash[_stat.source.name] = {'active': [], 'inactive': []}
    
            product_hash[_stat.source.name]['active'].append(_stat.active)
            product_hash[_stat.source.name]['inactive'].append(_stat.inactive)
    
        """
        Result:
        _hash = {
            "msp": {
                "active": [12, 13, 10],      #10th, 11th, 12th months values
                "inactive": [12, 13, 10],
            },
            "tenants": {
                "active":   [11, 7, 6],      #10th, 11th, 12th months values
                "inactive": [8, 31, 10],
            },
            
        }
        """
    
        labels = []
        for i in distinct_months:
            labels.append(months[i])
    
        
        for src in sources:
            dashboard = product + ' - ' + src
    
            active_values   = product_hash[src]['active']
            inactive_values = product_hash[src]['inactive']
            datasets.append({
                'name'     : dashboard,
                'dataset'  : [{
                    'label': 'Active',
                    'data' : active_values,
                    'backgroundColor' : colors_codes['olive'],
                    'borderColor' : colors_codes['olive'],
                    'highlightFill' : 'rgba(151,187,205,0.75)',
                    'highlightStroke' : 'rgba(151,187,220,1)',
                },{
                    'label': 'Inactive',
                    'data' : inactive_values,
                    'backgroundColor' : colors_codes['red'],
                    'borderColor' : colors_codes['red'],
                    'highlightFill' : 'rgba(151,187,205,0.75)',
                    'highlightStroke' : 'rgba(151,187,205,1)',
                }]
    
            })

    context = {'chart_type': chart_type, 'options': str(json.dumps(options)), 'labels': str(json.dumps(labels)), 'data_sets': str(json.dumps(datasets))}
    return context
