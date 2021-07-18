from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (CategoryViewSet, CreateUser, GenreViewSet,
                    obtain_token, TitleViewSet, UserViewSet)

API_VERSION = 'v1'

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('categories',
                   CategoryViewSet, basename='categories')
v1_router.register('genres',
                   GenreViewSet, basename='genres')

#     r'posts/(?P<post_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )
# v1_router.register('follow', FollowViewSet, basename='follow')
# v1_router.register('group', GroupViewSet, basename='group')

urlpatterns = (
    path(f'{API_VERSION}/auth/email/',
         CreateUser.as_view(),
         name='create_user'),
    path(f'{API_VERSION}/token/',
         obtain_token,
         name='token_obtain'),
    path(f'{API_VERSION}/', include(v1_router.urls)),
)
