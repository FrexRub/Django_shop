# Generated by Django 5.1.2 on 2024-11-28 10:22

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shopapp', '0019_alter_sales_datefrom_alter_sales_dateto'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('delivery_type', models.CharField(choices=[('ordinary', 'Ordinary'), ('express', 'Express')], default='ordinary', max_length=8, verbose_name='Тип доставки')),
                ('payment_type', models.CharField(choices=[('online', 'Online'), ('someone', 'Someone')], default='online', max_length=7, verbose_name='Способ оплаты')),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Общая цена заказа')),
                ('status', models.CharField(max_length=15, verbose_name='Статус заказа')),
                ('city', models.CharField(blank=True, max_length=40, verbose_name='Город')),
                ('address', models.CharField(blank=True, max_length=80, verbose_name='Адрес доставки')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Покупатель')),
            ],
        ),
        migrations.CreateModel(
            name='OrderInfoBasket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_in_order', models.PositiveSmallIntegerField(default=0, verbose_name='Количество товара')),
                ('price_in_order', models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Цена')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order', verbose_name='Заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.product', verbose_name='Товар')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='basket',
            field=models.ManyToManyField(through='orders.OrderInfoBasket', to='shopapp.product', verbose_name='Товары из корзины'),
        ),
    ]
