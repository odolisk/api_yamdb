from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import TitleViewSet, CategoryViewSet, GenreViewSet


router = DefaultRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register('categories',
                CategoryViewSet, basename='categories')
router.register('genres',
                GenreViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(router.urls)),
]
