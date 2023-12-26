from django.urls import path

from blog.views import (
    profile_update_view,
    profile_detail_view,
    category_detail_view,
    post_delete_view,
    post_update_view,
    post_create_view,
    post_detail_view,
    comment_update_view,

    add_comment,
    delete_comment,
    # ProfileDetailView,
    # ProfileUpdateView,
    PostListView,
    # PostCreateView,
    # PostUpdateView,
    # PostDetailView,
    # PostDeleteView,
    # CategoryDetailView,
    # CommentUpdateView,
)


app_name = 'blog'

urlpatterns = [
    # posts
    path(
        'posts/<int:post_id>/',
        post_detail_view,  # post_detail_view PostDetailView.as_view()
        name='post_detail'
    ),
    path(
        '',
        PostListView.as_view(),
        name='index'
    ),
    path(
        'posts/create/',
        post_create_view,  # post_create_view PostCreateView.as_view()
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        post_update_view,  # post_update_view PostUpdateView.as_view()
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        # post_delete_view login_required(PostDeleteView.as_view())
        post_delete_view,
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/create_comment/',  # создать комментарий
        add_comment,
        name='add_comment'
    ),
    path(
        # обновить комментарий
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        comment_update_view,  # comment_update_view CommentUpdateView.as_view()
        name='edit_comment'
    ),
    path(
        # удалить комментарий
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        delete_comment,
        name='delete_comment'
    ),
    # category
    path(
        # category_detail_view CategoryDetailView.as_view()
        'category/<slug:category_slug>/',
        category_detail_view,
        name='category_posts'
    ),
    # profile
    path(
        'profile/<str:username>/',
        profile_detail_view,  # profile_detail_view ProfileDetailView.as_view()
        name='profile'
    ),
    path(
        'profile/<str:username>/edit/',
        profile_update_view,  # profile_update_view ProfileUpdateView.as_view()
        name='edit_profile'
    ),
]
