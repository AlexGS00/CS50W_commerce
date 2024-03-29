# Generated by Django 5.0.1 on 2024-02-09 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_user_listings_user_watchlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='listings',
            field=models.ManyToManyField(blank=True, related_name='listings', to='auctions.listing'),
        ),
        migrations.AlterField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to='auctions.listing'),
        ),
    ]
