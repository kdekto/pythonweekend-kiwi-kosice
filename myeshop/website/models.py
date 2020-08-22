from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()

    def __str__(self):
        return self.name


class Basket(models.Model):
    items = models.ManyToManyField(Item)

    def __str__(self):
        return str(self.id)


class Invoice(models.Model):
    ltc_address = models.CharField(max_length=200)
    amount_required = models.IntegerField()
    amount_paid = models.IntegerField()

    @property
    def paid(self):
        return self.amount_paid >= self.amount_required

    def __str__(self):
        return self.ltc_address


class ShippingAddress(models.Model):
    state = models.CharField(max_length=200)
    # city = models.CharField(max_length=200)
    # street = models.CharField(max_length=200)


class Order(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    shipping_address = models.OneToOneField(ShippingAddress, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
