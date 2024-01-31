from django.db import transaction
from rest_framework import serializers

from foodcartapp.models import OrderProduct, Order


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ('product', 'quantity')

    def create(self, validated_data, order: Order):
        return OrderProduct.objects.create(
            order=order,
            price=validated_data['product'].price,
            **validated_data
        )


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False, required=True)

    class Meta:
        model = Order
        fields = ('firstname', 'lastname', 'address', 'phonenumber', 'products')

    def create(self, validated_data):
        products = validated_data.pop('products')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for product in products:
                serializer = OrderProductSerializer(data=product)
                serializer.create(product, order)

            return order
