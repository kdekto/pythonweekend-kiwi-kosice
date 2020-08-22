import random
import string
from base64 import b64encode
from io import BytesIO

import bitcoin.rpc
import qrcode

from django import forms
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template import loader
from django.views.decorators.http import require_POST
from django.shortcuts import redirect

from .models import ShippingAddress, Invoice, Order, Basket, Item


class AddItemForm(forms.Form):
    item_id = forms.CharField()


class CreateOrderForm(forms.Form):
    street = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()


def get_basket(request):
    basket_id = request.COOKIES.get("basket_id")

    if basket_id is None:
        basket = Basket()
        basket.save()
        basket_id = basket.id

    return basket_id


def index(request):

    basket_id = get_basket(request)

    # basket_content = Basket.objects.filter(id=basket_id).items
    template = loader.get_template('website/index.html')
    context = {
        'items': Item.objects.order_by("name"),
        'basket_content': Basket.objects.get(id=basket_id).items.all()
    }

    response = HttpResponse(template.render(context, request))
    response.set_cookie("basket_id", basket_id)

    return response


@require_POST
def add_item(request):
    form = AddItemForm(request.POST)

    if form.is_valid():
        item_id = form.cleaned_data["item_id"]
        basket_id = request.COOKIES.get("basket_id")
        if basket_id is None:
            return HttpResponseBadRequest("Basket ID not set.")

        Basket.objects.get(id=basket_id).items.add(Item.objects.get(id=item_id))

        response = redirect("/website")
        return response
    else:
        return HttpResponseBadRequest("Something went wrong.")


def create_order(request):

    if request.method == 'POST':
        form = CreateOrderForm(request.POST)
        if form.is_valid():
            shipping_address = ShippingAddress(state=form.cleaned_data["state"])
            shipping_address.save()
            basket = Basket.objects.get(id=request.COOKIES.get("basket_id"))

            rpcclient = bitcoin.rpc.RawProxy(service_url='http://user:user@litecoind:19443')
            ltc_address = rpcclient.getnewaddress()

            amount_required = basket.items.aggregate(Sum("price"))["price__sum"]
            invoice = Invoice(ltc_address=ltc_address, amount_required=amount_required, amount_paid=0)
            invoice.save()

            order = Order(basket=basket, shipping_address=shipping_address, invoice=invoice)
            order.save()

            response = redirect("/website/payment")
            response.delete_cookie("basket_id")
            response.set_cookie("order_id", order.id)
            return response

    else:
        form = CreateOrderForm()
        return render(request, 'website/createOrder.html', {'form': form})


def payment(request):
    order_id = request.COOKIES.get("order_id")
    order = Order.objects.get(id=order_id)
    ltc_address = order.invoice.ltc_address

    rpcclient = bitcoin.rpc.RawProxy(service_url='http://user:user@litecoind:19443')
    amount_paid = rpcclient.getreceivedbyaddress(ltc_address)

    img = qrcode.make(f'litecoin://{ltc_address}?amount=1')

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = b64encode(buffered.getvalue()).decode()

    return render(request, 'website/payment.html', context={'img': img_str, "ltc_address": ltc_address, "amount_paid": amount_paid})
