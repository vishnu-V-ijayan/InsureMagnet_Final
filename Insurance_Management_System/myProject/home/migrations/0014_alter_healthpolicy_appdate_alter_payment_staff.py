# Generated by Django 4.2.5 on 2024-04-29 04:38

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0013_healthpolicy_payment_hmembers_claimrequest_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="healthpolicy",
            name="appdate",
            field=models.DateField(
                default=datetime.date(2024, 4, 29), verbose_name="Approval Date"
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="staff",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="home.staff",
                verbose_name="Staff",
            ),
        ),
    ]
