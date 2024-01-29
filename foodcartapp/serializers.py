from rest_framework import serializers

from foodcartapp.models import OrderProduct, Order


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ('product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ('firstname', 'lastname', 'address', 'phonenumber', 'products')
