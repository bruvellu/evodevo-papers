# Generated by Django 4.2.9 on 2024-01-14 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]
