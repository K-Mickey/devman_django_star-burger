# Generated by Django 3.2.15 on 2024-01-30 23:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderproduct_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderproduct',
            old_name='price',
            new_name='current_price',
        ),
    ]
