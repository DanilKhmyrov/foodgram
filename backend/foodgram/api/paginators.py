from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Кастомный пагинатор, позволяющий ограничивать
    количество элементов на странице.
    """

    page_size = 1
    page_size_query_param = 'limit'
