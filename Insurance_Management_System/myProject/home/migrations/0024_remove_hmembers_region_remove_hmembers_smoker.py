# Generated by Django 4.2.5 on 2024-05-13 02:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0023_hmembers_children"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hmembers",
            name="region",
        ),
        migrations.RemoveField(
            model_name="hmembers",
            name="smoker",
        ),
    ]
