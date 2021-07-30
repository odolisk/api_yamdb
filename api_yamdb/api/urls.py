from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet,
    ReviewViewSet, TitleViewSet, UserViewSet,
    create_user_or_get_code, obtain_token)

API_VERSION = 'v1'

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('categories',
                   CategoryViewSet, basename='categories')
v1_router.register('genres',
                   GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

auth_patterns = [
    path('email/', create_user_or_get_code, name='create_user'),
    path('token/', obtain_token, name='token_obtain'),
]

urlpatterns = (
    path(f'{API_VERSION}/auth/', include(auth_patterns)),
    path(f'{API_VERSION}/', include(v1_router.urls)),
)
