import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse

User = get_user_model()


class Tag(models.Model):
    """
    Модель тега для рецептов, которая содержит название и slug.
    """

    name = models.CharField('Название тега', max_length=32, unique=True)
    slug = models.SlugField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Только латинские буквы, цифры, дефис и подчеркивание.'
            ),
        ]
    )

    class Meta:
        """
        Мета-класс для модели Tag, указывающий название модели.
        """
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингредиента, содержащая название и единицу измерения.
    """

    name = models.CharField('Имя ингредиента', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        """
        Мета-класс для модели Ingredient, указывающий название модели
        и добавляющий уникальность комбинации названия и единицы измерения.
        """
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель рецепта, содержащая автора, название, текст описания,
    время приготовления, теги и связанные ингредиенты.
    """
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        blank=True)
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        blank=True)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    name = models.CharField('Название', max_length=256)
    text = models.TextField('Описание', blank=False)
    cooking_time = models.IntegerField(
        'Время приготовления (мин)', null=False, blank=False,
        validators=[
            MinValueValidator(
                1, message='Время приготовления должно быть >= 1 минуте.')
        ]
    )
    short_code = models.CharField(
        'Короткая ссылка', max_length=8, unique=True, blank=True, null=True)

    class Meta:
        """
        Мета-класс для модели Recipe, указывающий название модели и сортировку.
        """
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def save(self, *args, **kwargs):
        """
        Сохраняет короткий код.
        """
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    def generate_short_code(self):
        """
        Генерирует короткий код.
        """
        return uuid.uuid4().hex[:8]

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для рецепта.
        """
        if settings.DEBUG:
            # В режиме разработки используем путь с /api/
            return reverse('recipes-detail', kwargs={'pk': self.pk})
        else:
            # В режиме продакшена используем путь без /api/
            return reverse('recipes-detail', kwargs={'pk': self.pk})[4:]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для связи рецептов и ингредиентов,
    содержащая количество каждого ингредиента в рецепте.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes')
    amount = models.IntegerField('Количество')

    class Meta:
        """
        Мета-класс для модели RecipeIngredient, указывающий уникальность
        комбинации рецепта и ингредиента.
        """

        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount} '


class Favorite(models.Model):
    """
    Модель избранного, связывающая пользователя и рецепт,
    который добавлен в избранное.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        """
        Мета-класс для модели Favorite, указывающий уникальность
        комбинации пользователя и рецепта.
        """

        unique_together = ('user', 'recipe')
        verbose_name = 'Избранные'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    """
    Модель корзины покупок, связывающая пользователя и рецепт,
    который добавлен в корзину.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_shopping_cart')

    class Meta:
        """
        Мета-класс для модели ShoppingCart, указывающий уникальность
        комбинации пользователя и рецепта.
        """

        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
