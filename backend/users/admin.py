from django.contrib import admin
from django.utils.html import format_html

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """
    Кастомная админка для модели CustomUser с возможностью управления
    пользователями, включая отображение миниатюры
    аватара и количества подписчиков.
    """

    list_display = ('username', 'email', 'last_login',
                    'avatar_thumbnail', 'subscriber_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'subscribers')
    search_fields = ('username', 'email')
    list_editable = ('email',)
    ordering = ('username',)
    filter_horizontal = ('subscribers',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'email', 'first_name',
                       'last_name', 'password',
                       'avatar', 'avatar_thumbnail')
        }),
        ('Права доступа', {
            'fields': ('is_staff', 'is_superuser', 'is_active')
        }),
        ('Подписки', {
            'fields': ('subscribers', 'subscriber_count')
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    readonly_fields = ('avatar_thumbnail', 'subscriber_count')

    def avatar_thumbnail(self, obj):
        """
        Возвращает HTML-код для отображения миниатюры аватара пользователя
        в админке, если аватар загружен.
        """
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px;" />',
                obj.avatar.url)
        return 'Нет аватара'

    avatar_thumbnail.short_description = 'Аватар'

    def subscriber_count(self, obj):
        """
        Возвращает количество подписчиков пользователя.
        """
        return obj.subscribers.count()

    subscriber_count.short_description = 'Количество подписчиков'
