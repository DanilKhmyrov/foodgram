from django.http import HttpResponse
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet


from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, ShoppingCart, Tag, Recipe
from .serializers import (AvatarSerializer, CreateRecipeSerializer,
                          CustomUserSerializer, CustomUserCreateSerializer,
                          IngredientGETSerializer, RecipeOutputSerializer,
                          SubscriptionsSerializer, TagSerializer)
from .permissions import IsAuthorOrAdmin
from .paginators import CustomPageNumberPagination

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list', 'me']:
            return CustomUserSerializer
        elif self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'subscriptions':
            return CustomUserCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def manage_avatar(self, request, *args, **kwargs):
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
        subscribed_users = request.user.subscribed_to.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subscribed_users, request)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def subscribe(self, request, *args, **kwargs):
        current_user = request.user
        user_to_subscribe = self.get_object()

        if current_user == user_to_subscribe:
            return Response({"status": "Cannot subscribe to yourself."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if not current_user.subscribed_to.filter(id=user_to_subscribe.id).exists():

                recipes_limit = request.query_params.get('recipes_limit', None)
                if recipes_limit is not None:
                    try:
                        recipes_limit = int(recipes_limit)
                    except ValueError:
                        return Response({'error': 'recipes_limit должно быть целым числом.'},
                                        status=status.HTTP_400_BAD_REQUEST)

                recipes = user_to_subscribe.recipes.all()[:recipes_limit]
                current_user.subscribed_to.add(user_to_subscribe)
                return Response(SubscriptionsSerializer(user_to_subscribe, context={'request': request,
                                                                                    'recipes': recipes}).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": "Already subscribed."},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if current_user.subscribed_to.filter(id=user_to_subscribe.id).exists():
                current_user.subscribed_to.remove(user_to_subscribe)
                return Response({"status": "Unsubscribed successfully."},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"status": "You are not subscribed to this user."},
                                status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeOutputSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return CreateRecipeSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_link']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'destroy']:
            permission_classes = [IsAuthorOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        output_serializer = RecipeOutputSerializer(
            recipe, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
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
        recipe = self.get_object()
        link = request.build_absolute_uri(f"/s/{recipe.short_code}/")
        return Response({'short-link': link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def get_favorite(self, request, pk=None):
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
        recipe = self.get_object()
        user = request.user
        link = request.build_absolute_uri(recipe.image.url)
        if request.method == 'POST':
            shopping_cart, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response({'errors': 'Рецепт уже находится в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'id': shopping_cart.id,
                             'name': recipe.name,
                             'image': link,
                             'cooking_time': recipe.cooking_time
                             }, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                shopping_cart = ShoppingCart.objects.get(
                    user=user, recipe=recipe)
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response({'errors': 'Рецепт не найден в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
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

        content = "Список покупок:\n"
        for name, amount in ingredients.items():
            content += f"{name}: {amount} {ingredient.measurement_unit}\n"

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'

        return response


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientGETSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
