from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer


class LoginView(APIView):
    """Authenticate a user and establish a session (cookie-based)."""

    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        
        # CSRFトークンを取得してクッキーに設定
        csrf_token = get_token(request)
        
        print(
            f"[DEBUG] LoginView: user={user.username}, session_key={request.session.session_key}, csrf_token={csrf_token[:10]}..."
        )
        
        response = Response({"id": user.id, "username": user.username, "email": user.email})
        # CSRFクッキーを確実に設定
        response.set_cookie(
            'csrftoken',
            csrf_token,
            max_age=31449600,  # 1年
            httponly=False,
            samesite='Lax',
            secure=False  # 開発環境用（HTTPの場合）
        )
        # セッションIDも明示的に設定（念のため）
        response.set_cookie(
            'sessionid',
            request.session.session_key,
            max_age=86400,  # 24時間
            httponly=True,
            samesite='Lax',
            secure=False  # 開発環境用（HTTPの場合）
        )
        return response


class LogoutView(APIView):
    """Logout the current user and clear the session."""

    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class MeView(APIView):
    """Return the current authenticated user"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Debug logging for authentication troubleshooting
        print(
            f"[DEBUG] MeView: user={request.user}, authenticated={request.user.is_authenticated}"
        )
        print(f"[DEBUG] MeView: session_key={request.session.session_key}")
        print(f"[DEBUG] MeView: cookies={request.COOKIES}")

        user = request.user
        return Response({"id": user.id, "username": user.username, "email": user.email})


class CSRFTokenView(APIView):
    """CSRFトークンを取得するエンドポイント"""
    
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        csrf_token = get_token(request)
        return Response({"csrfToken": csrf_token})
