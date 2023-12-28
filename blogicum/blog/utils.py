from django.utils import timezone
from django.db.models import Count
from django.db.models.query import QuerySet

from blog.models import Post


def select_posts(for_public=False,
                 for_many=False,
                 **kwargs) -> QuerySet:
    posts = Post.objects.select_related(
        'location', 'author', 'category',
    )
    if for_public:
        now = timezone.now()
        posts = posts.filter(
            pub_date__lte=now,
            is_published=True,
            category__is_published=True,
        )
    if for_many:
        posts = posts.annotate(
            comment_count=Count(
                'comments'
            )).order_by('-pub_date')
    return posts.filter(**kwargs)
