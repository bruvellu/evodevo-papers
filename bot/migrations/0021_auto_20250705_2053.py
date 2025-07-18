# Generated by Django 5.2.3 on 2025-07-05 18:53

from django.db import migrations


def create_statuses(apps, schema_editor):
    Post = apps.get_model("bot", "Post")
    Client = apps.get_model("bot", "Client")
    Status = apps.get_model("bot", "Status")

    for post in Post.objects.all():
        for client in Client.objects.filter(is_active=True):
            status, created = Status.objects.get_or_create(post=post, client=client)
            status.save()


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0020_alter_status_response"),
    ]

    operations = [
        migrations.RunPython(create_statuses),
    ]
