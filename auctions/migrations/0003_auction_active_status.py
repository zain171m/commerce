# Generated by Django 4.2.2 on 2023-07-28 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_watchlist_comment_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='active_status',
            field=models.BooleanField(default=True),
        ),
    ]
