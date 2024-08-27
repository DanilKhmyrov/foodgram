import os


def user_directory_path(instance, filename):
    """
    Формирует путь для загрузки файлов пользователя.
    """
    ext = filename.split('.')[-1]
    filename = f'image_{instance.id}.{ext}'
    return os.path.join('users', filename)
