# Generated by Django 5.1.1 on 2024-11-10 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0006_client_is_active'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Client',
        ),
    ]
