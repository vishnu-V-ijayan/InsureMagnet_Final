# Generated by Django 4.2.5 on 2024-05-03 06:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0018_claimapprovals"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClaimApproval",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "approval_status",
                    models.CharField(max_length=50, verbose_name="Approval Status"),
                ),
                ("comment", models.TextField(verbose_name="Comment")),
                (
                    "approved_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="Approved Amount",
                    ),
                ),
                ("approval_date", models.DateField(verbose_name="Approval Date")),
                (
                    "claim_request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approvals",
                        to="home.claimrequest",
                        verbose_name="Request Number",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Claim Approval",
                "verbose_name_plural": "Claim Approvals",
            },
        ),
        migrations.DeleteModel(
            name="ClaimApprovals",
        ),
    ]
