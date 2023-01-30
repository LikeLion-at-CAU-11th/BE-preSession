from django.urls import path
from posts.views import *

urlpatterns = [
    path('', hello_world, name = 'hello_world'),
    path('posts/<int:id>/', get_post_detail, name="get_post_detail"),
]