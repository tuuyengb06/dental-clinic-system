from rest_framework import serializers
from .models import Doctor, WorkSchedule, Service

class DoctorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Doctor
        fields = '__all__'

class WorkScheduleSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.__str__', read_only=True)

    class Meta:
        model = WorkSchedule
        fields = '__all__'

class DentalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service  # Dùng đúng tên Service từ models.py
        fields = '__all__'