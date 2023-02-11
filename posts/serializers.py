from rest_framework import serializers
from .models import *

class PostSerializer(serializers.ModelSerializer):

  class Meta:
	# 어떤 모델을 시리얼라이즈할 건지
    model = Post
	# 모델에서 어떤 필드를 가져올지
	# 전부 가져오고 싶을 때
    fields = "__all__"
		
	# 추가
	# 가져올 필드를 지정해줄 수도 있다.
	# fields = ['writer', 'content']
	# 제외할 필드를 지정해줄 수도 있다.		
	# exclude = ['id']
	# create, update, delete는 안되고 read만 되는 필드를 선언할 수도 있다.(이름같이 변경되지 않아야하는 필드의 경우)
	# read_only_fields = ['writer']

class CommentSerializer(serializers.ModelSerializer):

  class Meta:
    model = Comment
    fields = "__all__"