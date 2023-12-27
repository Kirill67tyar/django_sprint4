from django.urls import path

from blog.views import (
    post_detail_view,
    profile_update_view,

    add_comment,
    PostProfileListView,
    ProfileUpdateView,
    PostListView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    CommentUpdateView,
    CommentDeleteView,
    PostByCategoryListView,
)


app_name = 'blog'

urlpatterns = [
    path(
        'posts/<int:post_id>/',
        post_detail_view,  # PostDetailView.as_view() post_detail_view
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
        PostByCategoryListView.as_view(),  # PostByCategoryListView CategoryDetailView
        name='category_posts'
    ),
    path(
        'profile/edit/',
        ProfileUpdateView.as_view(),  # profile_update_view ProfileUpdateView.as_view()
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/',
        PostProfileListView.as_view(),  # PostProfileListView ProfileDetailView
        name='profile'
    ),
]
