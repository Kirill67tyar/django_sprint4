from django.urls import path

from blog.views import (
    index,
    post_detail,
    add_comment,
    ProfileDetailView,
    ProfileUpdateView,
    PostListView,
    PostCreateView,
    PostUpdateView,
    PostDetailView,
    CategoryDetailView,
    CommentUpdateView,
)


app_name = 'blog'

urlpatterns = [
    # posts
    path('', PostListView.as_view(), name='index'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit_post/',
         PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/create_comment/',
         add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         CommentUpdateView.as_view(), name='edit_comment'),
    # category
    path('category/<slug:slug>/',
         CategoryDetailView.as_view(),
         name='category_posts'),
    # profile
    path('profile/<str:username>/', ProfileDetailView.as_view(), name='profile'),
    path('profile/<str:username>/edit/',
         ProfileUpdateView.as_view(), name='edit_profile'),
]
