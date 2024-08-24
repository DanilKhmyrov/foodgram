from django.db import models
from django.contrib.auth.models import AbstractUser
import os


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'image_{instance.id}.{ext}'
    return os.path.join('users', filename)


class CustomUser(AbstractUser):
    avatar = models.ImageField(
        upload_to=user_directory_path, null=True, blank=True)
    subscribers = models.ManyToManyField(
        'self',
        related_name='subscribed_to',
        symmetrical=False,
        blank=True
    )

    class Meta:
        """
        Мета-класс для модели User, указывающий название модели.
        """
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
