from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
urlpatterns = [
    #회원가입/로그인/로그아웃
    path('create/', RegisterView.as_view()),
    path('login/', AuthView.as_view()),
    #토큰
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # 구글 소셜로그인
    path('google/login', google_login, name = 'google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('google/login/finish/', GoogleLogin.as_view(), name = 'google_login_todjango'),
]