from django.conf import settings
from django.core.paginator import Paginator


def paginate(request, queryset):
    """Вернуть запрошенную страницу пагинатора."""
    return Paginator(queryset, settings.POSTS_BY_PAGE).get_page(
        request.GET.get('page')
    )
