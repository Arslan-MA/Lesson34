# Generated by Django 4.2.6 on 2023-10-20 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_buyhistory_alter_product_slug'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BuyHistory',
        ),
    ]