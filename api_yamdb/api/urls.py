from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from django.urls import include, path

# from api.views import
# CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet

API_VERSION = 'v1'

v1_router = DefaultRouter()
# v1_router.register('posts', PostViewSet, basename='posts')
# v1_router.register(
#     r'posts/(?P<post_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )
# v1_router.register('follow', FollowViewSet, basename='follow')
# v1_router.register('group', GroupViewSet, basename='group')

urlpatterns = [
    path(f'{API_VERSION}/token/',
         TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path(f'{API_VERSION}/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
    path(f'{API_VERSION}/', include(v1_router.urls)),
]
