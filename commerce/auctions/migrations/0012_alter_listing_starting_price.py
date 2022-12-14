# Generated by Django 4.0.5 on 2022-08-18 12:05

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_listing_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='starting_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
    ]
