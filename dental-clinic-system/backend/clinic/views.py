from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Appointment, Invoice, Patient, Tooth, ToothCondition
from .serializers import AppointmentSerializer, InvoiceSerializer, PatientSerializer, ToothConditionSerializer, ToothSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        query = self.request.query_params.get("search", "")
        if query:
            return self.queryset.filter(Q(full_name__icontains=query) | Q(patient_code__icontains=query) | Q(phone__icontains=query))
        return self.queryset

    @action(detail=True, methods=["get", "put", "patch"])
    def tooth_chart(self, request, pk=None):
        patient = self.get_object()
        if request.method == "GET":
            teeth = Tooth.objects.filter(dentition_type=patient.dentition_type)
            conditions = {item.tooth_id: item for item in ToothCondition.objects.filter(patient=patient)}
            return Response([{"id": tooth.id, "code": tooth.code, "condition": conditions.get(tooth.id).condition if tooth.id in conditions else "Healthy"} for tooth in teeth])
        serializer = ToothConditionSerializer(data={**request.data, "patient": patient.id}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        tooth = serializer.validated_data["tooth"]
        if tooth.dentition_type != patient.dentition_type:
            return Response({"detail": "Tooth does not belong to patient's dentition"}, status=400)
        condition, _ = ToothCondition.objects.update_or_create(patient=patient, tooth=tooth, defaults={"condition": serializer.validated_data["condition"], "note": serializer.validated_data.get("note", "")})
        return Response(ToothConditionSerializer(condition).data)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related("patient").all()
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        conflict = Appointment.objects.filter(
            room=data["room"], status__in=[Appointment.SCHEDULED, Appointment.CONFIRMED],
            start_at__lt=data["end_at"], end_at__gt=data["start_at"]
        ).exists()
        if conflict:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Room has an overlapping appointment"})
        serializer.save()

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        appointment = self.get_object(); appointment.status = Appointment.CONFIRMED; appointment.save(update_fields=["status"])
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = self.get_object(); appointment.status = Appointment.CANCELLED; appointment.save(update_fields=["status"])
        return Response(self.get_serializer(appointment).data)


class ToothViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tooth.objects.all(); serializer_class = ToothSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("patient").all(); serializer_class = InvoiceSerializer

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        invoice = self.get_object()
        amount = request.data.get("amount")
        from decimal import Decimal
        amount = Decimal(str(amount))
        if amount <= 0 or amount > invoice.balance:
            return Response({"detail": "Payment must be positive and not exceed balance"}, status=status.HTTP_400_BAD_REQUEST)
        invoice.paid_amount += amount
        invoice.status = Invoice.PAID if invoice.balance == 0 else Invoice.PARTIAL
        invoice.save(update_fields=["paid_amount", "status"])
        return Response(self.get_serializer(invoice).data)


class HealthViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"status": "ok", "service": "DMS API"})
