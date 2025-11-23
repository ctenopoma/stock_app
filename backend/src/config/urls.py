from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # API entrypoint - actual routes should be registered in backend/src/api/urls.py
    path("api/v1/", include("api.urls")),
]
