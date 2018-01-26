from django.contrib import admin

# Register your models here.
from .models import Period, Product, Source, Stats

admin.site.register(Period)
admin.site.register(Product)
admin.site.register(Source)
admin.site.register(Stats)
