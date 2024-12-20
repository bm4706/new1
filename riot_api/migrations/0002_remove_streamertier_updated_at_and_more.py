# Generated by Django 5.0.7 on 2024-11-25 00:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("riot_api", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="streamertier",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="streamertier",
            name="game_name",
            field=models.CharField(default="unknown_game", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="streamertier",
            name="tag_line",
            field=models.CharField(default="unknown_tag", max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="streamertier",
            name="rank",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="streamertier",
            name="summoner_name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="streamertier",
            name="tier",
            field=models.CharField(max_length=50),
        ),
    ]
