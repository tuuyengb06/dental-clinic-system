from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from appointments.ai_services import (
    AIServiceConfigurationError,
    AIServiceError,
    generate_generic_follow_up_text,
)
from appointments.models import FollowUpReminder, MedicalRecord
from appointments.sms_services import (
    SMSDeliveryUncertainError,
    SMSServiceConfigurationError,
    SMSServiceError,
    build_follow_up_message,
    send_sms,
    validate_sms_configuration,
)


class Command(BaseCommand):
    help = "Send consented, due dental follow-up reminders by SMS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show eligible reminders without contacting Gemini or Twilio.",
        )

    def handle(self, *args, **options):
        today = timezone.localdate()
        records = list(
            MedicalRecord.objects.filter(
                follow_up_date__lte=today,
                appointment__patient__sms_reminder_consent=True,
            )
            .select_related("appointment__patient")
            .order_by("follow_up_date", "id")
        )
        if options["dry_run"]:
            self.stdout.write(f"{len(records)} consented follow-up reminder(s) are due.")
            return
        if not records:
            self.stdout.write("No consented follow-up reminders are due.")
            return

        FollowUpReminder.objects.filter(
            status=FollowUpReminder.Status.SENDING,
            updated_at__lt=timezone.now() - timedelta(minutes=30),
        ).update(
            status=FollowUpReminder.Status.UNKNOWN,
            error_message="Previous send attempt stopped before its outcome was recorded.",
        )
        existing = {
            (delivery.medical_record_id, delivery.scheduled_for): delivery.status
            for delivery in FollowUpReminder.objects.filter(
                medical_record__in=records,
                scheduled_for__lte=today,
            )
        }
        unresolved = []
        eligible_records = []
        for record in records:
            state = existing.get((record.pk, record.follow_up_date))
            if state == FollowUpReminder.Status.UNKNOWN:
                unresolved.append(f"record {record.pk}: verify Twilio before retrying")
            elif state not in (FollowUpReminder.Status.SENT, FollowUpReminder.Status.SENDING):
                eligible_records.append(record)
        records = eligible_records
        if not records:
            if unresolved:
                raise CommandError(
                    f"{len(unresolved)} reminder(s) have an unknown SMS outcome. "
                    + "; ".join(unresolved)
                )
            self.stdout.write("No unsent consented follow-up reminders are due.")
            return

        try:
            validate_sms_configuration()
        except SMSServiceConfigurationError as error:
            raise CommandError(str(error)) from error

        try:
            generic_text = generate_generic_follow_up_text()
        except (AIServiceConfigurationError, AIServiceError) as error:
            raise CommandError(str(error)) from error

        sent = 0
        failed = []
        for record in records:
            scheduled_for = record.follow_up_date
            with transaction.atomic():
                delivery, created = FollowUpReminder.objects.select_for_update().get_or_create(
                    medical_record=record,
                    scheduled_for=scheduled_for,
                    defaults={"status": FollowUpReminder.Status.SENDING},
                )
                if not created:
                    if delivery.status != FollowUpReminder.Status.FAILED:
                        continue
                    claimed = FollowUpReminder.objects.filter(
                        pk=delivery.pk,
                        status=FollowUpReminder.Status.FAILED,
                    ).update(
                        status=FollowUpReminder.Status.SENDING,
                        error_message="",
                        updated_at=timezone.now(),
                    )
                    if not claimed:
                        continue

            unknown_error = None
            error = None
            try:
                message = build_follow_up_message(scheduled_for, generic_text)
                reference = send_sms(record.appointment.patient.phone, message)
            except SMSDeliveryUncertainError as send_error:
                unknown_error = send_error
            except (SMSServiceConfigurationError, SMSServiceError) as send_error:
                error = send_error
            else:
                FollowUpReminder.objects.filter(pk=delivery.pk).update(
                    status=FollowUpReminder.Status.SENT,
                    provider_reference=reference,
                    error_message="",
                    sent_at=timezone.now(),
                )
                sent += 1
                continue

            if unknown_error:
                FollowUpReminder.objects.filter(pk=delivery.pk).update(
                    status=FollowUpReminder.Status.UNKNOWN,
                    error_message=str(unknown_error)[:240],
                )
                unresolved.append(f"record {record.pk}: {unknown_error}")
                continue

            FollowUpReminder.objects.filter(pk=delivery.pk).update(
                status=FollowUpReminder.Status.FAILED,
                error_message=str(error)[:240],
            )
            failed.append(f"record {record.pk}: {error}")

        self.stdout.write(f"Sent {sent} follow-up reminder(s).")
        if failed or unresolved:
            errors = failed + unresolved
            raise CommandError(
                f"{len(errors)} reminder(s) need attention: " + "; ".join(errors)
            )
