from typing import Any

from django.urls import reverse, reverse_lazy
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse as HttpResponse
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
    DetailView,
)

from blog.utils import (
    check_belonging_profile,
    require_POST,
)
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

QUANTITY_POSTS = 5


def post_detail(request, post_id):
    posts_qs = Post.valid_posts.all()
    post = get_object_or_404(
        posts_qs,
        pk=post_id,
    )
    context = {
        'post': post,
    }
    return render(
        request,
        'blog/detail.html',
        context,
    )


def index(request):
    posts_qs = Post.valid_posts.all()[:QUANTITY_POSTS]
    context = {
        'post_list': posts_qs,
    }
    return render(
        request,
        'blog/index.html',
        context,
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = Post.valid_posts.filter(
        category=category,
    )
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(
        request,
        'blog/category.html',
        context,
    )


@require_POST
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentModelForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=post_id)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    form_class = CommentModelForm
    model = Comment

    def dispatch(self,
                 request: HttpRequest,
                 *args: Any,
                 **kwargs: Any) -> HttpResponse:
        get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
            author=request.user
        )
        return super().dispatch(request, *args, **kwargs)


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentModelForm
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    form_class = PostModelForm
    model = Post

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.object.pk
            }
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/create.html'
    form_class = PostModelForm
    model = Post

    def dispatch(self,
                 request: HttpRequest,
                 *args: Any,
                 **kwargs: Any) -> HttpResponse:
        get_object_or_404(
            Post,
            pk=kwargs['post_id'],
            author=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={
                'username': self.request.user.username
            }
        )

    def form_valid(self, form):
        form.isnstance.author = self.request.user
        return super().form_valid(form)


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    queryset = Post.valid_posts.all()


class ByPageMixin:

    @staticmethod
    def get_items_by_page(qs, request, **kwargs):
        # qs = klass.valid_posts.filter(
        #     **kwargs
        # )
        paginator = Paginator(qs, 10)
        page = request.GET.get('page', 1)
        return paginator.get_page(page)


class CategoryDetailView(ByPageMixin, DetailView):
    model = Category
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        posts = Post.valid_posts.filter(
            category=self.object
        )
        context['page_obj'] = self.get_items_by_page(
            posts,
            self.request,
        )
        return context


class ProfileDetailView(ByPageMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        posts = Post.valid_posts.filter(
            author=self.object
        )
        if self.request.user.pk == self.object.pk:
            posts = posts.filter()
            posts = Post.objects.filter(
                author=self.request.user
            ).select_related('location', 'author', 'category',)
        context['page_obj'] = self.get_items_by_page(
            posts,
            self.request,
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html',
    model = User
    form_class = UserModelForm

    @check_belonging_profile
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
