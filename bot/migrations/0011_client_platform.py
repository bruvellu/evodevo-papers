# Generated by Django 5.2.3 on 2025-06-30 20:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0010_feed_modified_post_modified"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="platform",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
