from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment as ScheduledAppointment
from .models import Invoice


class DashboardRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(input_formats=["%Y-%m-%d"])
    end_date = serializers.DateField(input_formats=["%Y-%m-%d"])
    group_by = serializers.ChoiceField(
        choices=("auto", "day", "month"),
        required=False,
        default="auto",
    )

    def to_internal_value(self, data):
        if set(data) - {"start_date", "end_date", "group_by"}:
            raise serializers.ValidationError(
                {"detail": "Only start_date, end_date, and group_by are supported."}
            )
        return super().to_internal_value(data)

    def validate(self, attrs):
        start_date = attrs["start_date"]
        end_date = attrs["end_date"]
        if end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be on or after start date."}
            )
        if (end_date - start_date).days >= 3653:
            raise serializers.ValidationError(
                {"end_date": "Date range must not exceed ten years."}
            )
        group_by = attrs["group_by"]
        if group_by == "auto":
            attrs["group_by"] = (
                "day" if (end_date - start_date).days < 90 else "month"
            )
        if attrs["group_by"] == "day" and (end_date - start_date).days >= 366:
            raise serializers.ValidationError(
                {"group_by": "Daily grouping is limited to ranges of one year or less."}
            )
        return attrs


class IsClinicAdministrator(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.user.is_superuser:
            return True
        profile = getattr(request.user, "clinic_profile", None)
        return bool(profile and profile.role.code == "ADMIN")


def _periods(start_date, end_date, group_by):
    if group_by == "month":
        current = start_date.replace(day=1)
        end_month = end_date.replace(day=1)
        periods = []
        while current <= end_month:
            periods.append(current.strftime("%Y-%m"))
            current = (
                current.replace(year=current.year + 1, month=1)
                if current.month == 12
                else current.replace(month=current.month + 1)
            )
        return periods

    return [
        (start_date + timedelta(days=offset)).isoformat()
        for offset in range((end_date - start_date).days + 1)
    ]


class RevenueVisitDashboardAPIView(APIView):
    permission_classes = [IsClinicAdministrator]

    def get(self, request):
        serializer = DashboardRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]
        group_by = serializer.validated_data["group_by"]
        current_timezone = timezone.get_current_timezone()
        range_start = timezone.make_aware(
            datetime.combine(start_date, time.min),
            current_timezone,
        )
        range_end = timezone.make_aware(
            datetime.combine(end_date + timedelta(days=1), time.min),
            current_timezone,
        )
        truncation = TruncMonth if group_by == "month" else TruncDate

        revenue_rows = (
            Invoice.objects.filter(
                status=Invoice.PAID,
                issued_at__gte=range_start,
                issued_at__lt=range_end,
            )
            .annotate(period=truncation("issued_at", tzinfo=current_timezone))
            .values("period")
            .annotate(total=Sum("total_amount"))
        )
        visit_rows = (
            ScheduledAppointment.objects.filter(
                status=ScheduledAppointment.Status.COMPLETED,
                appointment_date__gte=range_start,
                appointment_date__lt=range_end,
            )
            .annotate(period=truncation("appointment_date", tzinfo=current_timezone))
            .values("period")
            .annotate(total=Count("id"))
        )

        periods = _periods(start_date, end_date, group_by)
        revenue_by_period = {
            row["period"].strftime("%Y-%m" if group_by == "month" else "%Y-%m-%d"): row["total"]
            or Decimal("0.00")
            for row in revenue_rows
        }
        visits_by_period = {
            row["period"].strftime("%Y-%m" if group_by == "month" else "%Y-%m-%d"): row["total"]
            or 0
            for row in visit_rows
        }
        series = [
            {
                "period": period,
                "revenue": f"{revenue_by_period.get(period, Decimal('0.00')):.2f}",
                "visits": visits_by_period.get(period, 0),
            }
            for period in periods
        ]
        total_revenue = sum(
            (Decimal(point["revenue"]) for point in series),
            Decimal("0.00"),
        )
        total_visits = sum(point["visits"] for point in series)

        return Response(
            {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "group_by": group_by,
                "timezone": "Asia/Ho_Chi_Minh",
                "revenue_definition": "PAID invoice total_amount grouped by invoice issued_at.",
                "visit_definition": "Completed appointments grouped by appointment_date.",
                "total_revenue": str(total_revenue),
                "total_visits": total_visits,
                "series": series,
            },
            status=status.HTTP_200_OK,
        )
