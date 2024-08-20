from django.contrib import admin
from .models import (Favorite, ShoppingCart, Tag,
                     Ingredient, Recipe, RecipeIngredient)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 5


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fieldsets = (
        ('ОСНОВНЫЕ ПОЛЯ', {
            'fields': ('name', 'author', 'get_favorite_count')
        }),
        ('ДЕТАЛИ', {
            'fields': ('text', 'tags', 'cooking_time', 'image')
        }),
    )
    list_display = ('name', 'author', 'cooking_time',
                    'image', 'get_favorite_count')
    inlines = [RecipeIngredientInline]
    exclude = ('short_code',)
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    readonly_fields = ('get_favorite_count',)
    actions = ['favorite_count']

    def get_favorite_count(self, obj):
        return obj.favorited_by.count()

    get_favorite_count.short_description = 'В избранном у'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
