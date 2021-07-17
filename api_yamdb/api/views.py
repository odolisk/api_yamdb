import json

from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import SlidingToken

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from api.permissions import IsAdmin, IsAuthorOrReadOnly, IsModerator
from api.serializers import UserSerializer


ALLOWED_CHARS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
FROM_EMAIL = 'admin@YamDb.com'

User = get_user_model()


class CreateUser(APIView):
    """
    Create user with email from request an random password.
    Send mail with password as confirmation_code.
    User is not active yet.
    """
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
            is_active=False,
            role='user'
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
    """
    Takes email and confirmation_code from request and
    get user sliding token with confirmation_code as password.
    Make user active.
    """
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('confirmation_code')
    users = User.objects.filter(email=email)
    if not users:
        res = {'email': f'User with email {email} not found'}
        return Response(
            data=res,
            status=status.HTTP_400_BAD_REQUEST)

    user = users[0]
    is_user_email = email == user.email
    is_user_pass = user.check_password(password)

    if is_user_email and is_user_pass:
        token = SlidingToken.for_user(user)
        user.is_active = True
        user.save()
        return Response({'token': str(token)}, status=status.HTTP_202_ACCEPTED)

    res = {'confirmation_code': 'confirmation_code not valid'
                                f'for email: {email}'}
    return Response(
        data=res,
        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ('username',)
    permission_classes = (IsAdmin,)

    @action(methods=('get', 'patch'), detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        """
        Return user info on GET, and correct user profile on PATCH.
        """
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('get', 'patch', 'delete'), detail=False,
            url_path=r'(?P<username>\w+)', permission_classes=(IsAdmin,))
    def get_update_delete_by_username(self, request, username):
        """
        Get, change user info or delete user by username.
        """
        user = get_object_or_404(User, username=username)
        if request.method == 'GET':
            serializer = UserSerializer(user)
        elif request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        else:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.data, status=status.HTTP_200_OK)
