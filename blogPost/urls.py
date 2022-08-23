from django.urls import path
from blogPost.views import (

    create_blog_view,
    blog_view,
    CatListView,
    # single_post_view,
    edit_blog_view,
    comment_view,
    delete_post,
    like_view,
    SinglePostView,
)

app_name = 'blogPost'

urlpatterns = [

    path('create/', create_blog_view, name='create'),
    path('<slug>/edit', edit_blog_view, name='edit'),
    path('category/<category>', CatListView.as_view(), name='category'),
    # path('<slug:post>/', single_post_view, name='single_post'),
    path('<slug:slug>/', SinglePostView.as_view(), name='details'),
    path('<slug:post>/like/', like_view, name='like'),
    path('<slug:post>/comment/', comment_view, name='comment'),
    path('<slug:post>/delete/', delete_post, name='delete_post'),
    path('', blog_view, name='blog'),
]
