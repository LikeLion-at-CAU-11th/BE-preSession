from django.urls import path
from posts.views import *

urlpatterns = [
    path('<int:id>/', post_detail, name="post_detail"),
    path('new/', create_post, name="create_post"),
    path('', get_post_all, name="get_post_all"),
]