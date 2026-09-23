from django.contrib import admin
from .models import Appointment, Invoice, Patient, Tooth, ToothCondition

admin.site.register([Patient, Tooth, ToothCondition, Appointment, Invoice])
