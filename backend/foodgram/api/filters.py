from django_filters.rest_framework import filters, FilterSet
from django.db.models import Exists, OuterRef
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, Favorite, ShoppingCart

User = get_user_model()


class RecipeFilter(FilterSet):
    author = filters.NumberFilter(field_name='author_id')
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if value and request and request.user.is_authenticated:
            return queryset.filter(Exists(
                Favorite.objects.filter(
                    user=request.user, recipe=OuterRef('pk'))
            ))
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if value and request and request.user.is_authenticated:
            return queryset.filter(Exists(
                ShoppingCart.objects.filter(
                    user=request.user, recipe=OuterRef('pk'))
            ))
        return queryset


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
