# Generated by Django 4.2.9 on 2024-01-14 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='service',
            field=models.CharField(default='mastodon', max_length=50),
            preserve_default=False,
        ),
    ]
