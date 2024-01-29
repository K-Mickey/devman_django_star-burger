import phonenumber_field
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderPosition


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_serialized = request.data
    error_text = validate_order(order_serialized)
    if error_text:
        return Response(
            {'status': 'error', 'message': error_text},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    order = Order.objects.create(
        firstname=order_serialized['firstname'],
        lastname=order_serialized['lastname'],
        address=order_serialized['address'],
        phonenumber=order_serialized['phonenumber'],
    )

    for position in order_serialized['products']:
        product = Product.objects.get(id=position['product'])
        if not product:
            return Response(
                {'status': 'error', 'message': 'Продукт не найден'},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        OrderPosition.objects.create(
            order=order,
            product=Product.objects.get(id=position['product']),
            quantity=position['quantity'],
        )
    return Response({})


def validate_order(order_serialized) -> str | None:
    required_fields = ['firstname', 'lastname', 'address', 'phonenumber', 'products']

    not_present_fields = [field for field in required_fields if field not in order_serialized]
    if not_present_fields:
        return f"{', '.join(not_present_fields)} - полей нет в запросе."

    none_fields = [field for field in required_fields if order_serialized[field] is None]
    if none_fields:
        return f"{', '.join(none_fields)} - это none значения."

    empty_fields = [field for field in required_fields if not order_serialized[field]]
    if empty_fields:
        return f"{', '.join(empty_fields)} - это пустые значения."

    if isinstance(order_serialized['products'], str):
        return 'Продукты - это не список, а строка.̆'

    if not isinstance(order_serialized['firstname'], str):
        return 'Имя - это не строка.'

    return None
