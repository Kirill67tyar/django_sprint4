import datetime as dt

from django.db import models


class PublishedWithTimeStampModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class ValidPostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lte=dt.datetime.now(),
            is_published=True,
            category__is_published=True,
        ).select_related('location', 'author', 'category',)
