from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("projects/new/", views.project_create, name="project_create"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/edit/", views.project_edit, name="project_edit"),
    path("projects/<int:pk>/members/add/", views.add_member, name="add_member"),
    path("projects/<int:pk>/tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    path("tasks/<int:pk>/status/", views.task_status, name="task_status"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("notifications/", views.notifications, name="notifications"),
    path("profile/", views.profile, name="profile"),
]
