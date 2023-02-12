from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Post
import json

# Create your views here.

"""
# 스터디 1주차
def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status': 200,
            'success': True,
            'message': '메시지 전달 성공!',
            'data': "Hello world",
        })
"""


"""
# 스터디 2주차
@require_http_methods(["GET"])
def get_post_detail(request, id):
    post = get_object_or_404(Post, pk=id)
    category_json = {
        "id": post.id,
        "writer": post.writer,
        "content": post.content,
        "category": post.category,
    }

    return JsonResponse({
        'status': 200,
        'message': '게시글 조회 성공',
        'data': category_json
    })
"""



# Django: FBV(함수 기반 뷰)
@require_http_methods(["POST"])
def create_post(request):
    # 새로운 게시글을 작성하는 view
    body = json.loads(request.body.decode('utf-8'))

    new_post = Post.objects.create(
        writer = body['writer'],
        title = body['title'],
        content = body['content'],
        category = body['category']
    )

    new_post_json = {
        "id": new_post.id,
        "writer": new_post.writer,
        "title": new_post.title,
        "content": new_post.content,
        "category": new_post.category
    }

    return JsonResponse({
        'status': 200,
        'message': '게시글 목록 조회 성공',
        'data': new_post_json
    })
    


@require_http_methods(["GET"])
def get_post_all(request):
    # 모든 게시글을 조회하는 view
    post_all = Post.objects.all()
    
    post_json_all = []
    for post in post_all:
        post_json = {
            "id": post.id,
            "writer": post.writer,
            "title": post.title,
            "category": post.category,
            "created_at": post.created_at
        }
        post_json_all.append(post_json)
    
    return JsonResponse({
        'status': 200,
        'message': '게시글 목록 조회 성공',
        'data': post_json_all
    })


@require_http_methods(["GET", "PATCH", "DELETE"])
def post_detail(request, id):
    if request.method == "GET":
        post = get_object_or_404(Post, pk=id)
        
        post_json = {
            "id": post.id,
            "writer": post.writer,
            "title": post.title,
            "content": post.content,
            "category": post.category,
        }

        return JsonResponse({
            'status': 200,
            'message': '게시글 조회 성공',
            'data': post_json
        })

    elif request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8'))
        update_post = get_object_or_404(Post, pk=id)

        update_post.title = body['title']
        update_post.content = body['content']
        update_post.save()

        update_post_json = {
            "id": update_post.id,
            "writer": update_post.writer,
            "title": update_post.title,
            "content": update_post.content,
            "category": update_post.category,
        }

        return JsonResponse({
            'status': 200,
            'message': '게시글 수정 성공',
            'data': update_post_json
        })


    elif request.method == "DELETE":
        delete_post = get_object_or_404(Post, pk=id)
        delete_post.delete()

        return JsonResponse({
                'status': 200,
                'message': '게시글 삭제 성공',
                'data': None
        })