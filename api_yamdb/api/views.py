import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from .filters import TitleFilter
from .models import Category, Genre, Title, Review
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          CommentAndReviewPermissions)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, ReviewSerializer,
    TitleWriteSerializer, TitleReadSerializer, UserSerializer
)

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
        user_exist = User.objects.filter(email=email)
        if user_exist:
            return Response(
                {'email': 'Данный email уже зарегистрирован'},
                status=status.HTTP_400_BAD_REQUEST)
        password = get_random_string(
            length=10,
            allowed_chars=ALLOWED_CHARS)
        User.objects.create_user(
            email=email,
            username=email,
            password=password,
            is_active=True,
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
@permission_classes([permissions.AllowAny, ])
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
        token = RefreshToken.for_user(user)
        user.is_active = True
        user.save()
        return Response({'token': str(token.access_token)},
                        status=status.HTTP_202_ACCEPTED)

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
    lookup_field = 'username'

    @action(methods=('get', 'patch'), detail=False,
            permission_classes=[permissions.IsAuthenticated])
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


class ListCreateDestroyAPIView(

    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class CategoryViewSet(ListCreateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(ListCreateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleWriteSerializer
        return TitleReadSerializer


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = (CommentAndReviewPermissions,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(
            author=self.request.user,
            review=review)


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = (CommentAndReviewPermissions,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def create(self, request, *args, **kwargs):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        review = Review.objects.filter(author=self.request.user,
                                       title=title)
        if review.exists():
            return Response(
                {'Отзыв': 'Вы уже оставляли отзыв'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, title)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, title):
        serializer.save(
            author=self.request.user,
            title=title)
