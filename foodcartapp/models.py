from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field import modelfields


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def total_price(self):
        return self.annotate(
            price=Sum(F('products__current_price') * F('products__quantity'))
        ).exclude(status=StatusOrder.complete)

    def available_restaurants(self):
        menu_items = RestaurantMenuItem.objects.\
            select_related('restaurant', 'product').filter(availability=True)
        for order in self:
            products = list(
                order.products.all().values_list('product', flat=True)
            )
            available_items = menu_items.filter(product_id__in=products)\
                .distinct()
            order.available_restaurants = {
                item.restaurant for item in available_items
            }
        return self


class StatusOrder(models.TextChoices):
    create = 'create', 'Создан'
    cooking = 'cooking', 'Готовится'
    deliver = 'deliver', 'Доставляется'
    complete = 'complete', 'Завершен'


class PayOrder(models.TextChoices):
    cash = 'cash', 'Наличные'
    card = 'card', 'Карта'


class Order(models.Model):
    status = models.CharField(
        verbose_name='Статус',
        max_length=10,
        choices=StatusOrder.choices,
        default=StatusOrder.create,
        db_index=True,
    )
    payment_method = models.CharField(
        verbose_name='Способ оплаты',
        max_length=10,
        choices=PayOrder.choices,
        default=PayOrder.cash,
        db_index=True,
    )
    firstname = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )
    lastname = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    phonenumber = modelfields.PhoneNumberField(
        verbose_name='Номер телефона',
    )
    address = models.CharField(
        max_length=200,
        verbose_name='Адрес',
        db_index=True,
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name='Ресторан',
        related_name='orders',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Время создания',
        db_index=True,
        default=timezone.now,
    )
    called_at = models.DateTimeField(
        verbose_name='Время звонка',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name='Время доставки',
        blank=True,
        null=True,
        db_index=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )
    current_price = models.DecimalField(
        verbose_name='Цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
