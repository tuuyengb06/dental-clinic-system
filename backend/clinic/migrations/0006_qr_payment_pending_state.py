from django.db import migrations, models
from django.db.models import F
from django.utils import timezone


def populate_payment_created_at(apps, schema_editor):
    Payment = apps.get_model("clinic", "Payment")
    Payment.objects.filter(
        created_at__isnull=True,
        paid_at__isnull=False,
    ).update(created_at=F("paid_at"))
    Payment.objects.filter(created_at__isnull=True).update(created_at=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0005_payment_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("COMPLETED", "Completed"),
                ],
                default="COMPLETED",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="paid_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="payment",
            name="bank_id",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="payment",
            name="bank_account_number",
            field=models.CharField(blank=True, default="", max_length=25),
        ),
        migrations.AddField(
            model_name="payment",
            name="bank_account_name",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.RunPython(
            populate_payment_created_at,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="payment",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
