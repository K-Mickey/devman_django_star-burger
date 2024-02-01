# Generated by Django 3.2.15 on 2024-02-01 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('create', 'Создан'), ('cooking', 'Готовится'), ('deliver', 'Доставляется'), ('complete', 'Завершен')], db_index=True, default='create', max_length=10, verbose_name='Статус'),
        ),
    ]