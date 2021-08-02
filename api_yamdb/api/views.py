from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings
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
    ReviewSerializer, TitleReadSerializer, TitleWriteSerializer,
    UserAuthSerializer, UserObtainTokenSerializer, UserSerializer
)


@api_view(('POST',))
@permission_classes([permissions.AllowAny])
def create_user_or_get_code(request):
    """
    Create user with email from request an random password.
    Send mail with password as confirmation_code.
    User is not active yet.
    """
    serializer = UserAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')

    user, created = User.objects.get_or_create(
        email=email
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail('Запрос confirmation_code для YamDB',
              f'Ваш confirmation_code: {confirmation_code}',
              from_email=settings.FROM_EMAIL,
              recipient_list=(email,))
    content = {'email': email}
    return Response(content, status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes([permissions.AllowAny])
def obtain_token(request):
    """
    Takes email and confirmation_code from request and
    get user sliding token with confirmation_code as password.
    Make user active.
    """
    serializer = UserObtainTokenSerializer(data=request.data)
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
    user.save()
    return Response({'token': str(token)},
                    status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
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
        if request.method in permissions.SAFE_METHODS:
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user, data=request.data, partial=True)
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
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-id')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrCanCreateOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
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

    def perform_create(self, serializer, *args, **kwargs):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(
            author=self.request.user,
            title=title)
