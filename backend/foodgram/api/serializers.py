import base64
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator

from .models import Ingredient, Recipe, RecipeIngredient, Tag
User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError("This field is required.")
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        if not value:
            raise serializers.ValidationError('This field is required.')
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError('Only image files are allowed.')
        return value


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already in use.')
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'avatar', 'is_subscribed')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return obj.subscribers.filter(id=request.user.id).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientWithAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(validators=[MinValueValidator(1)])


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInputSerializer(many=True, required=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(), required=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('view').action == 'create':
            self.fields['image'].required = True
        else:
            self.fields['image'].required = False

    def validate_tags(self, value):
        # Проверка на пустые теги
        if not value:
            raise serializers.ValidationError('Tags are required')

        # Проверка на уникальность тегов
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Tags should be unique')

        # Проверка существования тегов в базе данных
        existing_tags = Tag.objects.filter(
            id__in=value).values_list('id', flat=True)
        missing_tags = set(value) - set(existing_tags)

        if missing_tags:
            raise serializers.ValidationError(
                f'Tags with ids {missing_tags} do not exist.')
        return value

    def validate_ingredients(self, value):
        """Валидация ингредиентов"""
        if not value:
            raise serializers.ValidationError('Ingredients data is required')

        unique_ingredient_ids = set()
        for ingredient_data in value:
            ingredient_id = ingredient_data['id']

            if ingredient_id in unique_ingredient_ids:
                raise serializers.ValidationError(
                    f'Duplicate ingredient with id {ingredient_id} found.')

            unique_ingredient_ids.add(ingredient_id)

            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ingredient with id {ingredient_id} does not exist.'
                )

        return value

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop(
            'ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=request.user, **validated_data)
        self._create_recipe_ingredients(recipe, ingredients_data)

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                {'tags': 'This field is required.'})
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'ingredients': 'This field is required.'})
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        if 'image' in validated_data:
            instance.image = validated_data.get('image', instance.image)

        instance.save()

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._create_recipe_ingredients(instance, ingredients_data)

        instance.tags.set(tags_data)

        return instance

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        """Утилита для создания объектов модели RecipeIngredient."""
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)


class RecipeOutputSerializer(serializers.ModelSerializer):
    ingredients = IngredientWithAmountSerializer(
        source='recipe_ingredients', many=True)
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        user = request.user
        if request and user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        user = request.user
        if request and user.is_authenticated:
            return obj.in_shopping_cart.filter(user=user).exists()
        return False


class SubRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerializer):
    recipes = SubRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + \
            ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Access the context to retrieve the recipes passed from the view
        recipes = self.context.get('recipes', [])
        representation['recipes'] = SubRecipeSerializer(
            recipes, many=True).data
        return representation
