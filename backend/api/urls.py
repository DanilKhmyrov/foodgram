from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    # Аутентификация и управление токенами
    path('auth/token/login/', TokenCreateView.as_view(),
         name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(),
         name='logout'),
    # Пользовательские маршруты
    path('users/', CustomUserViewSet.as_view(
        {'get': 'list', 'post': 'create'}),
        name='customuser-list'),
    path('users/me/', CustomUserViewSet.as_view({'get': 'me'}),
         name='customuser-me'),
    path('users/<int:id>/', CustomUserViewSet.as_view(
        {'get': 'retrieve'}),
        name='customuser-detail'),
    path('users/me/avatar/', CustomUserViewSet.as_view(
        {'put': 'manage_avatar', 'delete': 'manage_avatar'}),
        name='avatar-manage'),
    # Подписки
    path('users/<int:id>/subscribe/',
         CustomUserViewSet.as_view(
             {'post': 'subscribe', 'delete': 'subscribe'}
         ),
         name='subscribe'),
    path('users/subscriptions/',
         CustomUserViewSet.as_view({'get': 'subscriptions'}),
         name='subscriptions'),
    # Управление паролем
    path('users/set_password/',
         CustomUserViewSet.as_view({'post': 'set_password'}),
         name='set_password'),
]
