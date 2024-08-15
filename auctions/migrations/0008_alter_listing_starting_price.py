# Generated by Django 5.0.7 on 2024-08-14 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_listing_starting_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='starting_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]