from rest_framework import generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from apps.core.viewsets import BaseViewSet
from apps.core.permissions import BusinessOwnerPermission
from apps.core.exceptions import success_response, error_response
from .models import UserProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, UserProfileSerializer, UserBusinessRegistrationSerializer
)

User = get_user_model()


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, BusinessOwnerPermission]
    search_fields = ['email', 'first_name', 'last_name']
    filterset_fields = ['is_active', 'locale']
    
    def get_queryset(self):
        if hasattr(self.request, 'business') and self.request.business:
            return self.request.business.users.all()
        return User.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserBusinessRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return success_response(
            data={
                'user': UserSerializer(result['user']).data,
                'business_slug': result['business'].slug,
                'business_name': result['business'].name
            },
            message="Registration successful"
        )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return success_response(message="Password changed successfully")
        return error_response(
            message="Password change failed",
            errors=serializer.errors
        )
