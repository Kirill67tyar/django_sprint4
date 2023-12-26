from typing import Any

from django.db.models import Count
from django.urls import reverse, reverse_lazy
# from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
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
    # check_belonging_profile,
    require_post,
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


class ByPageMixin:

    @staticmethod
    def get_items_by_page(qs, request, **kwargs):
        # qs = klass.valid_posts.filter(
        #     **kwargs
        # )
        paginator = Paginator(qs, 10)
        page = request.GET.get('page', 1)
        return paginator.get_page(page)


@require_post
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentModelForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(
        'blog:post_detail',
        post_id=post_id,
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        author=request.user,
    )
    context = {
        'comment': comment,
    }
    if request.method == 'POST':
        comment.delete()
        return redirect(
            'blog:post_detail',
            post_id=post_id,
        )
    return render(
        request,
        'blog/comment.html',
        context,
    )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'comment_id'

    def dispatch(self,
                 request: HttpRequest,
                 *args: Any,
                 **kwargs: Any) -> HttpResponse:
        post = get_object_or_404(
            Post,
            pk=kwargs['post_id'],
        )
        get_object_or_404(
            Comment,
            post=post,
            pk=kwargs['comment_id'],
            author=request.user
        )
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    form_class = CommentModelForm
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self) -> str:
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk, }
        )

    def get(self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        post = get_object_or_404(
            Post,
            pk=kwargs['post_id'],
        )
        get_object_or_404(
            Comment,
            post=post,
            pk=kwargs['comment_id'],
            author=request.user
        )
        return super().get(request, *args, **kwargs)


@login_required
def comment_update_view(request, post_id, comment_id):
    instance = get_object_or_404(
        Comment,
        pk=comment_id,
    )
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentModelForm(
        data=request.POST or None,
        instance=instance,
    )
    context = {
        'form': form,
        'comment': instance,
    }
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(
        request,
        'blog/comment.html',
        context=context,
    )


class CustomLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                'blog:post_detail',
                post_id=kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)

# ---------- post detail ------------------ START


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    # queryset = Post.objects.all().select_related(
    # 'location', 'author', 'category',).prefetch_related('comments')

    # def dispatch(self, request, *args, **kwargs):
    #     self.author = get_object_or_404(
    #         User,
    #         pk=kwargs['user_id'],
    #     )
    #     return super().dispatch(request, *args, **kwargs)

    # def get_queryset(self) -> QuerySet[Any]:
    #     qs = super().get_queryset().select_related(
    #         'location', 'author', 'category',).prefetch_related('comments')
    #     return qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentModelForm
        context['comments'] = self.object.comments.all()
        return context


def post_detail_view(request, post_id):
    posts_qs = Post.objects.all()
    post = get_object_or_404(
        posts_qs,
        pk=post_id,
    )
    if request.user != post.author:
        posts_qs = Post.valid_posts.all()
        post = get_object_or_404(
            posts_qs,
            pk=post_id,
        )
    context = {
        'post': post,
        'form': CommentModelForm(),
        'comments': post.comments.all(),
    }
    return render(
        request,
        'blog/detail.html',
        context,
    )


# ---------- post detail ------------------ END
# ---------- post create ------------------ START


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    form_class = PostModelForm
    # model = Post
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


@login_required
def post_create_view(request):
    form = PostModelForm(
        data=request.POST or None,
        files=request.FILES or None,
    )
    context = {
        'form': form,
    }
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)

    return render(
        request,
        'blog/create.html',
        context=context,
    )

# ---------- post create ------------------ END
# ---------- post update ------------------ START


class PostUpdateView(UpdateView):  # LoginRequiredMixin
    template_name = 'blog/create.html'
    form_class = PostModelForm
    model = Post
    pk_url_kwarg = 'post_id'

    def post(self, request, post_id, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect(
                'blog:post_detail',
                post_id=post_id
            )
        get_object_or_404(
            Post,
            pk=post_id,
            author=request.user
        )
        return super().post(request, post_id, *args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)

    def dispatch(self,
                 request: HttpRequest,
                 *args: Any,
                 **kwargs: Any) -> HttpResponse:
        # if not request.user.is_authenticated:
        #     return redirect(
        #         'blog:post_detail',
        #         post_id=kwargs['post_id']
        #     )
        # get_object_or_404(
        #     Post,
        #     pk=kwargs['post_id'],
        #     author=request.user
        # )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={
                'username': self.request.user.username
            }
        )


@login_required
def post_update_view(request, post_id):
    instance = get_object_or_404(
        Post,
        pk=post_id,
    )
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostModelForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=instance,
    )
    context = {
        'form': form,
    }
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(
        request,
        'blog/create.html',
        context=context,
    )
# ---------- post update ------------------ END
# ---------- post list ------------------ START


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    queryset = Post.valid_posts.annotate(
        comment_count=Count('comments')).order_by('-pub_date')

# ---------- post list ------------------ END
# ---------- post delete ------------------ START


class PostDeleteView(DeleteView):  # LoginRequiredMixin
    model = Post
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self,
                 request: HttpRequest,
                 *args: Any,
                 **kwargs: Any) -> HttpResponse:
        get_object_or_404(
            Post,
            pk=kwargs['post_id'],
            author=request.user,
        )
        # if not request.user.is_anonymous and post.author == request.user:
        #     return super().dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
        # raise Http404('asd')


@login_required
def post_delete_view(request, post_id):
    instance = get_object_or_404(
        Post,
        pk=post_id
    )
    if request.user != instance.author:
        return redirect('blog:index')
    form = PostModelForm(
        instance=instance,
    )
    context = {
        'form': form,
    }
    if request.method == 'POST':
        instance.delete()
        # form.instance.delete()
        return redirect(
            to='blog:index'
            # to='blog:profile',
            # username=request.user.username,
        )
    return render(
        request,
        'blog/create.html',  # шаблон для удаления - create
        context=context,
    )

# ---------- post delete ------------------ END
# ---------- category detail ------------------ START


class CategoryDetailView(ByPageMixin, DetailView):
    model = Category
    template_name = 'blog/category.html'
    queryset = Category.objects.filter(
        is_published=True).prefetch_related('posts')

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


def category_detail_view(request, category_slug):

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = Post.valid_posts.filter(
        category=category,
    )
    paginator = Paginator(post_list, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)
# ---------- category detail ------------------ END


# ---------- profile detail ------------------ START


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
        if not self.request.user.is_anonymous:
            if self.request.user.pk == self.object.pk:
                posts = Post.objects.filter(
                    author=self.request.user
                ).select_related('location', 'author', 'category',)
        context['page_obj'] = self.get_items_by_page(
            posts,
            self.request,
        )
        return context


def profile_detail_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.valid_posts.filter(author=user).order_by('-pub_date')
    if request.user.pk == user.pk:
        posts = Post.objects.filter(
            author=request.user
        ).select_related(
            'location',
            'author',
            'category',
        ).order_by('-pub_date')
    posts = posts.annotate(comment_count=Count('comments'))
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    context = {

        'page_obj': page_obj,
        'profile': user,
    }
    return render(request, 'blog/profile.html', context)

# ---------- profile detail ------------------ END
# ---------- profile update ------------------ START


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html',
    model = User
    form_class = UserModelForm
    slug_url_kwarg = 'username'
    slug_field = 'username'

    # @check_belonging_profile
    # def dispatch(self,
    #              request: HttpRequest,
    #              *args: Any,
    #              **kwargs: Any) -> HttpResponse:
    #     return super().dispatch(request, *args, **kwargs)


def profile_update_view(request, username):
    user = get_object_or_404(User, username=username)
    if user != request.user:
        return redirect('login')
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

# ---------- profile update ------------------ END
