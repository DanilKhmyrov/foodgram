from rest_framework.permissions import BasePermission


class IsAuthorOrAdmin(BasePermission):
    """
    Пермишн, предоставляющий доступ только автору объекта или администратору.
    """

    message = 'Только Админ и Автор имеют доступ.'

    def has_permission(self, request, view):
        """
        Проверяет, аутентифицирован ли пользователь.
        """
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Предоставляет доступ, если пользователь является
        автором объекта или администратором.
        """
        return request.user == obj.author or request.user.is_staff
