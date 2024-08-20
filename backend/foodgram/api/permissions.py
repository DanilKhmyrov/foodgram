from rest_framework.permissions import BasePermission


class IsAuthorOrAdmin(BasePermission):
    message = 'Только Админ и Автор имеею доступ.'

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author or request.user.is_staff
