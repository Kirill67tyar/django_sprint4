from django.urls import include, path

from blog.views import (
    post_detail_view,
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

post_urls = [
    path(
        '<int:post_id>/',
        post_detail_view,
        name='post_detail'
    ),
    path(
        'create/',
        PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        '<int:post_id>/edit/',
        PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/create_comment/',
        add_comment,
        name='add_comment'
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        CommentDeleteView.as_view(),
        name='delete_comment'
    ),

]


urlpatterns = [
    path(
        '',
        PostListView.as_view(),
        name='index'
    ),
    path(
        'posts/',
        include(post_urls),
    ),
    path(
        'category/<slug:category_slug>/',
        PostByCategoryListView.as_view(),
        name='category_posts'
    ),
    path(
        'edit/',
        ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/',
        PostProfileListView.as_view(),
        name='profile',
    ),
]
