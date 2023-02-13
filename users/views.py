from django.shortcuts import render
from .models import Member
from .serializers import AuthSerializer, RegisterSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import RefreshToken, TokenObtainPairSerializer
from django.contrib.auth import authenticate

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
