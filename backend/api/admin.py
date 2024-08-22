from django.contrib import admin
from django.utils.html import format_html

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """
    Inline-класс для редактирования ингредиентов в рецепте
    прямо на странице редактирования рецепта.
    """

    model = RecipeIngredient
    extra = 5


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Кастомная админка для модели Recipe с возможностью
    редактирования рецепта и его ингредиентов, а также
    отображением количества добавлений в избранное.
    """

    fieldsets = (
        ('ОСНОВНЫЕ ПОЛЯ', {
            'fields': ('name', 'author')
        }),
        ('ДЕТАЛИ', {
            'fields': ('text', 'tags', 'cooking_time', 'image')
        }),
    )
    list_display = ('name', 'author', 'cooking_time',
                    'image_thumbnail', 'get_favorite_count')
    inlines = [RecipeIngredientInline]
    exclude = ('short_code',)
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def image_thumbnail(self, obj):
        """
        Возвращает HTML-код для отображения картинки в админке,
        если она загружена.
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px;" />',
                obj.image.url)
        return 'Нет картинки'

    image_thumbnail.short_description = 'Изображение'

    def get_favorite_count(self, obj):
        """
        Возвращает количество добавлений рецепта в избранное.
        """
        return obj.favorited_by.count()

    get_favorite_count.short_description = 'Количество в избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Кастомная админка для модели Tag.
    """

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Кастомная админка для модели Ingredient.
    """

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Кастомная админка для модели Favorite.
    """

    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Кастомная админка для модели ShoppingCart.
    """

    list_display = ('user', 'recipe')
