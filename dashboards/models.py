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
from django.db import models
from django.utils import six, timezone
import calendar

# Create your models here.
class EnumField(models.Field):
    """
    A field class that maps to ENUM type.
    
    Usage:
    class BookCover(Model):
        color = EnumField(choices=['red', 'green', 'blue'])
    
    class Book(Model):
        color = EnumField(choices=[
          ('red', 'Bright Red'),
          ('green', 'Vibrant Green'),
          'blue',  # human readable name will be set to "blue"
        ])
    """
    
    def __init__(self, *args, **kwargs):
        if 'choices' not in kwargs or len(kwargs['choices']) == 0:
            raise ValueError('"choices" argument must be be a non-empty list')
        
        choices = []
        for choice in kwargs['choices']:
            if isinstance(choice, tuple):
                choices.append(choice)
            elif isinstance(choice, six.string_types):
                choices.append((choice, choice))
            else:
                raise TypeError(
                    'Invalid choice "{choice}". '
                    'Expected string or tuple as elements in choices'.format(
                        choice=choice,
                    )
                )
        kwargs['choices'] = choices
        super(EnumField, self).__init__(*args, **kwargs)
    
    
    def db_type(self):
        return "enum({0})".format( ','.join("'%s'" % col for col, _ in self.choices))



'''
To get current Year:
MySQL: select year(curdate());
SQLite: SELECT strftime('%s','now');

curr_year = int(time.strftime('%Y'))
'''
class Period(models.Model):
    months_array = list((k, v) for k,v in enumerate(calendar.month_name))
    del months_array[0]
    
    year  = models.IntegerField(default=timezone.now().year)
    month = models.IntegerField(choices=months_array)
    
    class Meta:
        db_table = "period"
        unique_together = ('year', 'month',)
    
    def __str__(self):
        return "year: {}, month: {}".format(self.year, self.month)


class Source(models.Model):
    
    name = models.CharField(max_length=10, choices=[('msp', 'Service Providers'), ('tenants', 'Tenants'), ('users', 'Users'), ('resources', 'Resources')], unique=True)
    
    class Meta:
        db_table = "sources"
    
    def __str__(self):
        return self.name


class Product(models.Model):
    
    name = models.CharField(max_length=10, choices=[('ITOM', 'ITOM'), ('IMONSITE', 'IMONSITE')], unique=True)
    #sources = models.ManyToManyField(Sources, through='Stats')
    
    class Meta:
        db_table = "products"
    
    def __str__(self):
        return self.name


class Stats(models.Model):
    
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    source   = models.ForeignKey(Source, on_delete=models.CASCADE)
    period   = models.ForeignKey(Period, on_delete=models.CASCADE)
    
    active   = models.IntegerField()
    inactive = models.IntegerField()
    
    class Meta:
        db_table = "product_stats"
        unique_together = ('period', 'product', 'source',)
    
    #def __str__(self):
    #    return "product: {}, source: {}, active: {}, inactive: {}".format(self.product.__str__(), self.source.__str__(), self.active, self.inactive)
