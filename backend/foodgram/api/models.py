import uuid
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.urls import reverse


User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=32, unique=True)
    slug = models.SlugField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Слаг может содержать только буквы, цифры, дефисы и подчеркивания.'
            ),
        ]
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Имя ингредиента', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, related_name='recipes', verbose_name='Автор', on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты', blank=True)
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги', blank=True)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    name = models.CharField('Название', max_length=256)
    text = models.TextField('Описание', blank=False)
    cooking_time = models.IntegerField(
        'Время приготовления (мин)', null=False, blank=False,
        validators=[
            MinValueValidator(
                1, message='Время приготовления должно быть больше или равно 1 минуте.')
        ]
    )
    short_code = models.CharField(
        'Короткая ссылка', max_length=8, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    def generate_short_code(self):
        return uuid.uuid4().hex[:8]

    def get_absolute_url(self):
        return reverse('recipes-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    amount = models.IntegerField('Количество')

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"

    def __str__(self):
        return f'{self.ingredient.name} ({self.ingredient.measurement_unit}) - {self.amount} '


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранные'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f"Избранные пользователя {self.user.username}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_shopping_cart')

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f"Список покупок пользователя {self.user.username}"
