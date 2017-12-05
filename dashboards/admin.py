from django.contrib import admin

# Register your models here.
from .models import ProductStats, Period, Product, Source, Stats

admin.site.register(ProductStats)

admin.site.register(Period)
admin.site.register(Product)
admin.site.register(Source)
admin.site.register(Stats)
