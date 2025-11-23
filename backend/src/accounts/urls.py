from django.urls import path

from .views import CSRFTokenView, LoginView, LogoutView, MeView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("csrf/", CSRFTokenView.as_view(), name="csrf"),
]
