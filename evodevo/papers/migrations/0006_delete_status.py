# Generated by Django 5.1.1 on 2024-11-10 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0005_alter_status_post'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Status',
        ),
    ]
