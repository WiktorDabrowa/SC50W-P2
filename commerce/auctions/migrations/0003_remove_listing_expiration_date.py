# Generated by Django 4.0.5 on 2022-08-08 06:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing_is_open'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='expiration_date',
        ),
    ]
