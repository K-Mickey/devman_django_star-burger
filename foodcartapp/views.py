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
    error_text = None
    try:
        products = order_serialized['products']
    except KeyError:
        error_text = 'Продуктов нет.'
    else:
        if products is None:
            error_text = 'Продукты - это null.̆'
        elif not products:
            error_text = 'Продукты - пустой список.̆'
        elif isinstance(products, str):
            error_text = 'Продукты - это не список, а строка.̆'

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

    for position in products:
        OrderPosition.objects.create(
            order=order,
            product=Product.objects.get(id=position['product']),
            quantity=position['quantity'],
        )
    return Response({})
