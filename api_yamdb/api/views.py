import json

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import SlidingToken

from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

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


@api_view(('POST',))
@csrf_exempt
@permission_classes([permissions.AllowAny])
def obtain_token(request):
    data = json.loads(request.body)
    email = data['email']
    user = get_object_or_404(User, email=email)
    password = data['confirmation_code']
    if email == user.email and user.check_password(password):
        token = SlidingToken.for_user(user)
        user.is_active = True
        user.save()
        return Response({'token': str(token)}, status=status.HTTP_202_ACCEPTED)
    res = {'code': 404, 'message': 'User not found password not valid.'}
    return Response(data=json.dumps(res), status=status.HTTP_404_NOT_FOUND)
