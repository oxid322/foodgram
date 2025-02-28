from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
        Разрешения для рецептов:
        - GET: Разрешено всем пользователям.
        - POST: Разрешено только авторизованным пользователям.
        - PATCH, DELETE: Разрешено только автору рецепта.
    """

    def has_permission(self, request, view):
        # Разрешаем GET-запросы всем
        if request.method == 'GET':
            return True

        # Разрешаем POST-запросы только авторизованным пользователям
        if request.method == 'POST':
            return request.user and request.user.is_authenticated

        # Для PUT и DELETE проверяем, что пользователь авторизован
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET-запросы всем
        if request.method == 'GET':
            return True

        # Разрешаем PUT и DELETE только автору рецепта
        if request.method in ['PATCH', 'DELETE']:
            return obj.author == request.user

        # По умолчанию запрещаем доступ
        return False
