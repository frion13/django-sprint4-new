from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_posts(
    manager=Post.objects,
    filter_published=False,
    annotate_comments=False,
):
    """Вернуть оптимизированный queryset публикаций."""
    posts = manager.select_related('author', 'category', 'location')
    if filter_published:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
    if annotate_comments:
        posts = posts.annotate(comment_count=Count('comments'))
    return posts.order_by('-pub_date')
