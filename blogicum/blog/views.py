import datetime as dt
from typing import Any

from django.utils import timezone
from django.urls import reverse_lazy
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.http import Http404, HttpRequest
from django.http.response import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    DeleteView,
)

from blog.utils import select
from blog.forms import (
    UserModelForm,
    PostModelForm,
    CommentModelForm,
)
from blog.models import (
    Post,
    Category,
    Comment,
)


User = get_user_model()
QUANTITY_POSTS = 10


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self,
                 request: HttpRequest,
                 *args: Any,
                 **kwargs: Any) -> HttpResponse:
        instance = get_object_or_404(
            self.model,
            pk=kwargs['comment_id'],
            post_id=kwargs['post_id'],
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostUpdateDeleteMixin:
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self,
                 request: HttpRequest,
                 *args: Any,
                 **kwargs: Any) -> HttpResponse:
        instance = get_object_or_404(
            Post,
            pk=kwargs['post_id'],
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostListMixin:
    paginate_by = QUANTITY_POSTS
    queryset = select(
        Post.valid_posts.all(),
        for_public=True,
        for_many=True
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentModelForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(
        'blog:post_detail',
        post_id=post_id,
    )


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    success_url = reverse_lazy('blog:index')


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentModelForm

    def get_success_url(self) -> str:

        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk, }
        )


def post_detail_view(request, post_id):
    posts_qs = Post.valid_posts.all().prefetch_related('comments')
    post = get_object_or_404(
        posts_qs,
        pk=post_id,
    )
    if request.user != post.author:
        now = timezone.make_aware(
            dt.datetime.now(), timezone.get_default_timezone())
        if (
            (not post.is_published)
            or (not post.category.is_published)
                or (post.pub_date > now)
        ):
            raise Http404('Page not found')
    context = {
        'post': post,
        'form': CommentModelForm(),
        'comments': post.comments.select_related('author'),
    }
    return render(
        request,
        'blog/detail.html',
        context,
    )


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    form_class = PostModelForm
    pk_url_kwarg = 'post_id'

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={
                'username': self.object.author.username
            }
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostUpdateDeleteMixin, UpdateView):
    form_class = PostModelForm

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.object.pk
            }
        )


class PostDeleteView(LoginRequiredMixin, PostUpdateDeleteMixin, DeleteView):
    success_url = reverse_lazy('blog:index')


class PostListView(PostListMixin, ListView):
    template_name = 'blog/index.html'


class PostByCategoryListView(PostListMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        posts = super().get_queryset()
        self.category = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return posts.filter(
            category=self.category,
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostProfileListView(ListView):
    queryset = Post.valid_posts.all()
    template_name = 'blog/profile.html'
    paginate_by = QUANTITY_POSTS

    def get_queryset(self) -> QuerySet[Any]:
        posts = super().get_queryset()
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        params = {
            'for_many': True,
            'author': self.profile,
        }
        if self.request.user != self.profile:
            params['for_public'] = True
        return select(
            posts,
            **params
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = UserModelForm
    model = User

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={
                'username': self.object.username,
            }
        )

    def get_object(self, queryset: QuerySet[Any] or None = ...) -> Model:
        obj = get_object_or_404(
            self.model,
            pk=self.request.user.pk
        )
        return obj
