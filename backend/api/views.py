from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .paginators import CustomPageNumberPagination
from .permissions import IsAuthorOrAdmin
from .serializers import (AvatarSerializer, CreateRecipeSerializer,
                          CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientGETSerializer, RecipeOutputSerializer,
                          SubRecipeSerializer, SubscriptionsSerializer,
                          TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    Кастомный ViewSet для управления пользователями, включает
    методы для подписки, работы с аватаром и получения подписок.
    """

    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Возвращает queryset всех пользователей.
        """
        return User.objects.all()

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от действия.
        """
        if self.action in ['retrieve', 'list', 'me']:
            return CustomUserSerializer

        if self.action in ['create', 'subscriptions']:
            return CustomUserCreateSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        """
        Возвращает права доступа в зависимости от действия.
        """
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def manage_avatar(self, request, *args, **kwargs):
        """
        Управляет аватаром пользователя: добавление и удаление.
        """
        user = request.user
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {'error': 'This field is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = AvatarSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            avatar_url = serializer.data['avatar']
            full_avatar_url = request.build_absolute_uri(avatar_url)
            return Response(
                {'avatar': full_avatar_url},
                status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.avatar.delete(save=True)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def subscriptions(self, request, *args, **kwargs):
        """
        Возвращает список подписок текущего пользователя.
        """
        subscribed_users = (request.user.subscribed_to
                            .prefetch_related('recipes')
                            .all())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subscribed_users, request)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def subscribe(self, request, *args, **kwargs):
        """
        Подписка и отписка от пользователя.
        """
        current_user = request.user
        user_to_subscribe = self.get_object()

        if request.method == 'POST':
            recipes_limit = request.query_params.get('recipes_limit', None)
            if recipes_limit is not None:
                try:
                    recipes_limit = int(recipes_limit)
                except ValueError:
                    return Response(
                        {'error': 'recipes_limit должно быть целым числом.'},
                        status=status.HTTP_400_BAD_REQUEST)

            recipes = user_to_subscribe.recipes.all()[:recipes_limit]

            serializer = SubscriptionsSerializer(
                instance=user_to_subscribe,
                context={
                    'request': request, 'recipes': recipes})

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if current_user.subscribed_to.filter(
                    id=user_to_subscribe.id).exists():
                current_user.subscribed_to.remove(user_to_subscribe)
                return Response({'status': 'Вы отписались от пользователя.'},
                                status=status.HTTP_204_NO_CONTENT)

            return Response({'status': 'Вы не подписаны на пользователя.'},
                            status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для получения списка тегов и тега.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    """
    ViewSet для управления рецептами, включает создание,
    обновление, удаление и добавление в избранное и корзину покупок.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeOutputSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от действия.
        """
        if self.action in ['create', 'partial_update']:
            return CreateRecipeSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        """
        Возвращает контекст сериализатора с дополнительными данными.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        """
        Возвращает права доступа в зависимости от действия.
        """
        if self.action in ['list', 'retrieve', 'get_link']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'destroy']:
            permission_classes = [IsAuthorOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет рецепт.
        """
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Создает новый рецепт.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        output_serializer = RecipeOutputSerializer(
            recipe, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление рецепта.
        """
        recipe = self.get_object()

        serializer = self.get_serializer(
            recipe, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        output_serializer = RecipeOutputSerializer(
            recipe, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """
        Возвращает короткую ссылку на рецепт.
        """
        recipe = self.get_object()
        link = request.build_absolute_uri(f'/s/{recipe.short_code}/')
        return Response({'short-link': link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def get_favorite(self, request, pk=None):
        """
        Добавление/удаление рецепта в избранное.
        """
        recipe = self.get_object()
        user = request.user
        link = request.build_absolute_uri(recipe.image.url)

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response({'errors': 'Рецепт уже находится в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'id': favorite.id,
                             'name': recipe.name,
                             'image': link,
                             'cooking_time': recipe.cooking_time
                             }, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response({'errors': 'Рецепт не найден в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        """
        Добавление/удаление рецепта в корзину покупок.
        """
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            shopping_cart, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response(
                    {'errors': 'Рецепт уже находится в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = SubRecipeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                shopping_cart = ShoppingCart.objects.get(
                    user=user, recipe=recipe)
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response(
                    {'errors': 'Рецепт не найден в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """
        Генерирует и возвращает текстовый файл со списком покупок.
        """
        shopping_cart = request.user.shopping_cart.all()

        ingredients = {}
        for item in shopping_cart:
            recipe = item.recipe
            for recipe_ingredient in recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient
                amount = recipe_ingredient.amount
                if ingredient.name in ingredients:
                    ingredients[ingredient.name] += amount
                else:
                    ingredients[ingredient.name] = amount

        content = 'Список покупок:\n'
        for name, amount in ingredients.items():
            content += f'{name}: {amount} {ingredient.measurement_unit}\n'

        response = HttpResponse(content, content_type='text/plain')
        conf = 'attachment; filename="shopping_cart.txt"'
        response['Content-Disposition'] = conf

        return response


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для получения списка ингредиентов и ингредиента.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientGETSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
