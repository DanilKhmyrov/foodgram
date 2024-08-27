from django.db import models
from django.contrib.auth.models import AbstractUser

from .utils import user_directory_path


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

    def __str__(self):
        return self.username
