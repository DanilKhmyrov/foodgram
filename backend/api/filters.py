from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from .models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    """
    Фильтр для рецептов, позволяющий фильтровать по автору, тегам,
    добавлению в избранное и наличию в корзине покупок.
    """

    author = filters.NumberFilter(field_name='author_id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрация рецептов, которые добавлены в избранное текущего юзера.
        """
        request = getattr(self, 'request', None)
        if value and request and request.user.is_authenticated:
            return queryset.filter(favorited_by__user=request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрация рецептов, которые добавлены в покупки текущего юзера.
        """
        request = getattr(self, 'request', None)
        if value and request and request.user.is_authenticated:
            return queryset.filter(in_shopping_cart__user=request.user)
        return queryset

    class Meta:
        """
        Мета-класс для указания модели и полей фильтрации.
        """

        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


class IngredientFilter(FilterSet):
    """
    Фильтр для ингредиентов, позволяющий фильтровать по имени.
    """

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        """
        Мета-класс для указания модели и полей фильтрации.
        """

        model = Ingredient
        fields = ['name']
