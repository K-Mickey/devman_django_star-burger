# Generated by Django 3.2.15 on 2024-01-30 22:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20240129_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена'),
            preserve_default=False,
        ),
    ]
