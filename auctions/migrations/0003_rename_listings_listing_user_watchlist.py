# Generated by Django 5.0.1 on 2024-02-05 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listings'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Listings',
            new_name='Listing',
        ),
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(related_name='watchlist', to='auctions.listing'),
        ),
    ]
