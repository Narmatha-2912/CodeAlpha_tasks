from django.contrib import admin
from django.urls import path, include
from workspace import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("", include("django.contrib.auth.urls")),
    path("", include("workspace.urls")),
]
