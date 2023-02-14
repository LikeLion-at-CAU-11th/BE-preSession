from django.shortcuts import redirect
#from .models import Member
from .serializers import AuthSerializer, RegisterSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import RefreshToken, TokenObtainPairSerializer
from django.contrib.auth import authenticate
# 소셜로그인
import os
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from rest_framework import status
from .models import *
from allauth.socialaccount.models import SocialAccount

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view

# 구글 소셜로그인 변수 설정
state = os.environ.get("STATE")
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'users/google/callback/'

class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=False):
            member = serializer.save(request)
            token = RefreshToken.for_user(member)
            refresh_token = str(token)
            access_token = str(token.access_token)

            res = Response(
                {
                    "member":serializer.data,
                    "message":"register success",
                    "token":{
                        "access_token":access_token,
                        "refresh_token":refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            return res
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthView(APIView):
    serializer_class = AuthSerializer

    def post(self, request):
        member = authenticate(username=request.data['username'], password=request.data['password'])
        #이미 회원가입한 유저인 경우
        if member is not None:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid(raise_exception=False):
                member = serializer.validated_data['member']
                access_token = serializer.validated_data['access_token']
                refresh_token = serializer.validated_data['refresh_token']
                res = Response(
                    {
                        "member":{
                            "id":member.id,
                            "email":member.email,
                            "age":member.age,
                        },
                        "message":"login success",
                        "token":{
                            "access_token":access_token,
                            "refresh_token":refresh_token,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
                res.set_cookie("access-token", access_token, httponly=True)
                res.set_cookie("refresh-token", refresh_token, httponly=True)
                return res
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else: 
            return Response('member account not exist', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        res = Response({
            "message":"logout success"
        }, status=status.HTTP_202_ACCEPTED)
        res.delete_cookie("access-token")
        res.delete_cookie("refresh-token")
        return res

# 구글 로그인
# 이 url로 들어가면 구글 로그인 창이 뜨고, 알맞은 아이디와 비밀번호를 입력하면 callback URI로 코드값이 들어간다.
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):

    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')

    # 1. 받은 코드로 구글에 access token 요청
    token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    
    ### 1-1. json으로 변환 & 에러 부분 파싱
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    ### 1-2. 에러 발생 시 종료
    if error is not None:
        raise JSONDecodeError(error)

    ### 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get('access_token')

    #################################################################

    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code

    ### 2-1. 에러 발생 시 400 에러 반환
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    ### 2-2. 성공 시 이메일 가져오기
    email_req_json = email_req.json()
    email = email_req_json.get('email')

    # return JsonResponse({'access': access_token, 'email':email})

    #################################################################

    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = Member.objects.get(email=email)

        
        # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        # 있는데 구글계정이 아니어도 에러
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/user/google/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)

        return JsonResponse(accept_json)
    

    except Member.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/user/google/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)

        return JsonResponse(accept_json)
        
    #except SocialAccount.DoesNotExist:
    	#User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
     #   return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
    
class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client