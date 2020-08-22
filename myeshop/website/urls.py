from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addItem', views.add_item, name='addItem'),
    path('createOrder', views.create_order, name='createOrder'),
    path('payment', views.payment, name='payment')
]
