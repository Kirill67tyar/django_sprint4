import datetime as dt
from typing import Any

from django.utils import timezone
from django.db.models import Count
from django.db.models.query import QuerySet


def select(queryset: QuerySet[Any],
           for_public=False,
           for_many=False,
           **kwargs) -> QuerySet:
    if for_public:
        NOW = timezone.make_aware(
            dt.datetime.now(),
            timezone.get_default_timezone()
        )
        queryset = queryset.filter(
            pub_date__lte=NOW,
            is_published=True,
            category__is_published=True,
        )
    if for_many:
        queryset = queryset.annotate(
            comment_count=Count(
                'comments'
            )).order_by('-pub_date')
    return queryset.filter(**kwargs)
