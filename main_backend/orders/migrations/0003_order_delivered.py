# Generated by Django 4.1.3 on 2022-11-20 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_cash_on_delivery_order_paid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivered',
            field=models.BooleanField(default=False),
        ),
    ]