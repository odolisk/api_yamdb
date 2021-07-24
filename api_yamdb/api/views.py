from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from .filters import TitleFilter
from .models import Category, Genre, Title, Review, User
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAdminModeratorAuthorOrCanCreateOrReadOnly)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleWriteSerializer, TitleReadSerializer,
    UserSerializer, UserAuthSerializer
)
from django.conf import settings

User = get_user_model()


@api_view(('POST',))
@permission_classes([permissions.AllowAny, ])
def create_user_or_get_code(request):
    """
    Create user with email from request an random password.
    Send mail with password as confirmation_code.
    User is not active yet.
    """
    serializer = UserAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    print(f'email: {email} ended')
    user, created = User.objects.get_or_create(
        email=email
    )
    print('boo')
    confirmation_code = default_token_generator.make_token(user)
    send_mail('Запрос confirmation_code для YamDB',
              f'Ваш confirmation_code: {confirmation_code}',
              from_email=settings.FROM_EMAIL,
              recipient_list=(email,))
    content = {'email': email}
    return Response(content, status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes([permissions.AllowAny, ])
def obtain_token(request):
    """
    Takes email and confirmation_code from request and
    get user sliding token with confirmation_code as password.
    Make user active.
    """
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    user = get_object_or_404(User, email=email)
    confirmation_code = serializer.validated_data['confirmation_code']
    valid = default_token_generator.check_token(user, confirmation_code)
    if not valid:
        res = {'confirmation_code': 'confirmation_code not valid'
                                    f'for email: {email}'}
        return Response(
            data=res,
            status=status.HTTP_400_BAD_REQUEST)

    token = AccessToken.for_user(user)
    user.is_active = True
    user.save()
    return Response({'token': str(token)},
                    status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ('username',)
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
            # serializer = UserSerializer(user)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(ListCreateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
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

    def get_rating(self, title):
        return title.reviews.aggregate(rating=Avg('score'))['rating']


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrCanCreateOrReadOnly,)

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
    permission_classes = (IsAdminModeratorAuthorOrCanCreateOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def create(self, request, *args, **kwargs):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        # review = Review.objects.filter(author=self.request.user,
        #                                title=title)
        # if review.exists():
        #     return Response(
        #         {'Отзыв': 'Вы уже оставляли отзыв'},
        #         status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        data._mutable = True
        data['title_id'] = title.id
        data['author_id'] = request.user.id
        data._mutable = False
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, title)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, title):
        serializer.save(
            author=self.request.user,
            title=title)
