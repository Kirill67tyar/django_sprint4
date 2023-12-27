from django.urls import path

from blog.views import (
    post_detail_view,

    add_comment,
    ProfileDetailView,
    ProfileUpdateView,
    PostListView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    CategoryDetailView,
    CommentUpdateView,
    CommentDeleteView,
)


app_name = 'blog'

urlpatterns = [
    path(
        'posts/<int:post_id>/',
        post_detail_view,
        name='post_detail'
    ),
    path(
        '',
        PostListView.as_view(),
        name='index'
    ),
    path(
        'posts/create/',
        PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/create_comment/',
        add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'category/<slug:category_slug>/',
        CategoryDetailView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/<str:username>/',
        ProfileDetailView.as_view(),
        name='profile'
    ),
    path(
        'profile/<str:username>/edit/',
        ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
]
