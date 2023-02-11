
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Post, Comment
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
# Create your views here.

def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'success' : True,
            'message' : '메시지 전달 성공!',
            'data' : "Hello world",
        })


@require_http_methods(["GET"])
def get_post_detail(request, id):
    post = get_object_or_404(Post, pk = id)
    category_json={
                "id"        : post.id,
                "writer"    : post.writer,
                "content" : post.content,
                "category" : post.category,
    }
        
    return JsonResponse({
                'status': 200,
                'message': '게시글 조회 성공',
                'data': category_json
            })

class PostList(APIView):
    def get(self, request, format=None):
        posts = Post.objects.all()
		# 많은 post들을 받아오려면 (many=True) 써줘야 한다! 이렇게 에러뜨는 경우가 생각보다 많다.
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_)
class PostDetail(APIView):
    def get(self,request,id):
        post = get_object_or_404(Post, id=id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self,request,id):
        post = get_object_or_404(Post, id=id)
        serializer = PostSerializer(post, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        post = get_object_or_404(Post, id=id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)