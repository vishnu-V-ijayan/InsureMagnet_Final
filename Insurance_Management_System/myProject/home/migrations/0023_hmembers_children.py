# Generated by Django 4.2.5 on 2024-05-08 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0022_agent_category_customer_healthplan_healthpolicy_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hmembers",
            name="children",
            field=models.IntegerField(default=0),
        ),
    ]
