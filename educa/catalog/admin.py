from django.contrib import admin
from .models import Product, ProductGroup, ProductAccess, Lesson


admin.site.register(Product)
admin.site.register(ProductGroup)
admin.site.register(ProductAccess)
admin.site.register(Lesson)