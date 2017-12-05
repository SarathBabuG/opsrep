# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-29 16:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0008_remove_products_source'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Products',
            new_name='Product',
        ),
        migrations.RenameModel(
            old_name='Sources',
            new_name='Source',
        ),
        migrations.AlterUniqueTogether(
            name='stats',
            unique_together=set([('period', 'product', 'source')]),
        ),
    ]
