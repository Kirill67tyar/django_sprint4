from functools import wraps

from django.http import Http404
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect

User = get_user_model()


def check_belonging_profile(func):
    """
    Декоратор, который проверяет в dispatch, 
    что профиль, который редактирует пользователь
    принадлежит ему
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        profile = get_object_or_404(
            User,
            username=kwargs['username'],
        )
        if request.user != profile:
            raise Http404('page not found')
        return func(self, request, *args, **kwargs)

    return wrapper


def require_POST(func):
    @wraps(func)
    def wrapper(request, pk, *args, **kwargs):
        if request.method == 'POST':
            return func(request, pk, *args, **kwargs)
        return HttpResponseNotAllowed('Only POST method allowed')
    return wrapper
