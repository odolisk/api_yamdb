from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

from api.serializers import UserSerializer, YamDBTokenObtainPairSerializer

ALLOWED_CHARS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
FROM_EMAIL = 'admin@YamDb.com'

User = get_user_model()


class CreateUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        email = request.data.get('email')
        password = get_random_string(
            length=10,
            allowed_chars=ALLOWED_CHARS)
        User.objects.create_user(
            email=email,
            username=email,
            password=password,
            is_active=False
        )
        send_mail('Request code for YamDB',
                  f'Your confirmation_code: {password}',
                  from_email=FROM_EMAIL,
                  recipient_list=(email,))
        content = {'email': email}
        return Response(content, status=status.HTTP_200_OK)


class YamDBTokenObtainPairView(TokenObtainPairView):

    serializer_class = YamDBTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        password = self.request.get('confirmation_code')
        serializer.save(password=password)
