from django.contrib import admin

from .models import Item, Basket, Order, Invoice, ShippingAddress

# Register your models here.

admin.site.register(Item)
admin.site.register(Basket)
admin.site.register(Order)
admin.site.register(Invoice)
admin.site.register(ShippingAddress)
