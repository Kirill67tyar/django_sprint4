import datetime as dt
from typing import Any

from django.utils import timezone
from django.db.models import Count
from django.urls import reverse_lazy
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.http import Http404, HttpRequest
from django.core.paginator import Paginator
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


class ProfileMixin:
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'


class ByPageMixin:
    @staticmethod
    def get_items_by_page(qs, request):
        paginator = Paginator(qs, 10)
        page = request.GET.get('page', 1)
        return paginator.get_page(page)


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
    posts_qs = Post.objects.all().select_related(
        'location', 'author', 'category',).prefetch_related('comments')
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


class PostUpdateView(LoginRequiredMixin, PostUpdateDeleteMixin, UpdateView):
    form_class = PostModelForm

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.object.pk
            }
        )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = QUANTITY_POSTS
    queryset = Post.valid_posts.annotate(
        comment_count=Count('comments')).order_by('-pub_date')


class PostDeleteView(LoginRequiredMixin, PostUpdateDeleteMixin, DeleteView):  # LoginRequiredMixin
    success_url = reverse_lazy('blog:index')


class PostByCategoryListView(ListView):
    # queryset = Post.valid_posts.none
    template_name = 'blog/category.html'
    paginate_by = QUANTITY_POSTS
    model = Post

    def get_queryset(self) -> QuerySet[Any]:
        posts = super().get_queryset()
        self.category = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return posts.filter(
            category=self.category,
            pub_date__lte=dt.datetime.now(),
            is_published=True,
            category__is_published=True,
        ).select_related('location', 'author', 'category',)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


# class CategoryDetailView(ByPageMixin, DetailView):
#     model = Category
#     template_name = 'blog/category.html'
#     slug_url_kwarg = 'category_slug'
#     queryset = Category.objects.filter(
#         is_published=True).prefetch_related('posts')

#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:

#         context = super().get_context_data(**kwargs)
#         posts = self.object.posts.filter(
#             pub_date__lte=dt.datetime.now(),
#             is_published=True,
#             category__is_published=True,
#         ).select_related('location', 'author', 'category',)
#         context['page_obj'] = self.get_items_by_page(
#             posts,
#             self.request,
#         )
#         return context

class PostProfileListView(ListView):
    # queryset = Post.valid_posts.none
    template_name = 'blog/profile.html'
    paginate_by = QUANTITY_POSTS
    model = Post

    def get_queryset(self) -> QuerySet[Any]:
        posts = super().get_queryset()
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if self.request.user == self.profile:
            return posts.filter(author=self.profile).select_related(
                'location', 'author', 'category',
            ).order_by('-pub_date').annotate(comment_count=Count('comments'))
        return Post.valid_posts.filter(
            author=self.profile
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


# class ProfileDetailView(ByPageMixin, ProfileMixin, DetailView):
#     template_name = 'blog/profile.html'
#     context_object_name = 'profile'

#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context = super().get_context_data(**kwargs)
#         posts = Post.valid_posts.filter(
#             author=self.object
#         ).order_by('-pub_date').annotate(comment_count=Count('comments'))
#         if self.request.user.pk == self.object.pk:
#             posts = Post.objects.filter(
#                 author=self.request.user
#             ).select_related(
#                 'location', 'author', 'category',
#             ).order_by('-pub_date').annotate(comment_count=Count('comments'))
#         context['page_obj'] = self.get_items_by_page(
#             posts,
#             self.request,
#         )
#         return context


class ProfileUpdateView(LoginRequiredMixin, ProfileMixin, UpdateView):
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


@login_required
def profile_update_view(request):
    username = request.user.username
    user = get_object_or_404(User, username=username)
    form = UserModelForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect(
            'blog:profile',
            username=username
        )
    context = {
        'form': form
    }
    return render(request, 'blog/user.html', context)
