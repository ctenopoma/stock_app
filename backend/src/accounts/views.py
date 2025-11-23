from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer


class LoginView(APIView):
    """Authenticate a user and establish a session (cookie-based)."""

    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        print(
            f"[DEBUG] LoginView: user={user.username}, session_key={request.session.session_key}"
        )
        return Response({"id": user.id, "username": user.username, "email": user.email})


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
