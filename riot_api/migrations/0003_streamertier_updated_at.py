# Generated by Django 5.0.7 on 2024-11-25 00:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("riot_api", "0002_remove_streamertier_updated_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="streamertier",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]