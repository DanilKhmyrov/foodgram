from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def redirect_to_recipe(request, short_code):
    """
    Перенаправляет пользователя на страницу рецепта по короткому коду.
    """
    recipe = get_object_or_404(Recipe, short_code=short_code)
    return redirect(recipe.get_absolute_url())
