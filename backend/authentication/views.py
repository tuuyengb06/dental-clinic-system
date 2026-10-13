from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = {
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'role': user.role,
        }
        return Response(
            {'message': 'Registration successful.', 'user': user_data},
            status=status.HTTP_201_CREATED,
        )


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        role_codes = {
            'Admin': 'ADMIN',
            'Doctor': 'DENTIST',
            'Receptionist': 'RECEPTIONIST',
            'Patient': 'PATIENT',
        }
        display_name = ' '.join(part for part in (user.first_name, user.last_name) if part).strip() or user.username
        return Response({
            'id': user.pk,
            'username': user.username,
            'display_name': display_name,
            'email': user.email,
            'phone': user.phone,
            'role': role_codes.get(user.role, 'PATIENT'),
        })
