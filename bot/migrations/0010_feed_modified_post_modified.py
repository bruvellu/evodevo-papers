# Generated by Django 5.2.3 on 2025-06-28 11:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0009_feed_created"),
    ]

    operations = [
        migrations.AddField(
            model_name="feed",
            name="modified",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="post",
            name="modified",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
