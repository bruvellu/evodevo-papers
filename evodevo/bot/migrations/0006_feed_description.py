# Generated by Django 5.1.3 on 2024-11-14 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
