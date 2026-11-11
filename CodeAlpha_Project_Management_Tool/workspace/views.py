from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import RegisterForm, ProjectForm, TaskForm, CommentForm
from .models import Project, Task, Comment, Notification
from .utils import broadcast_project

User = get_user_model()

def home(request):
    return redirect("dashboard") if request.user.is_authenticated else redirect("login")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to TaskFlow. Your account is ready!")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    projects = Project.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
    tasks = Task.objects.filter(project__in=projects)
    context = {
        "projects": projects,
        "total_tasks": tasks.count(),
        "completed_tasks": tasks.filter(status="done").count(),
        "in_progress_tasks": tasks.filter(status="doing").count(),
        "my_tasks": tasks.filter(assignee=request.user).exclude(status="done")[:6],
        "recent_notifications": Notification.objects.filter(recipient=request.user)[:5],
    }
    return render(request, "workspace/dashboard.html", context)

@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.members.add(request.user)
            messages.success(request, "Project created successfully.")
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, "workspace/form_page.html", {"form": form, "heading": "Create a project", "back_url": "dashboard"})

def get_accessible_project(user, pk):
    return get_object_or_404(Project.objects.filter(Q(owner=user) | Q(members=user)).distinct(), pk=pk)

@login_required
def project_detail(request, pk):
    project = get_accessible_project(request.user, pk)
    tasks = project.tasks.select_related("assignee", "created_by")
    return render(request, "workspace/project_detail.html", {"project": project, "tasks": tasks, "columns": [("todo", "To do"), ("doing", "In progress"), ("done", "Completed")]})

@login_required
def project_edit(request, pk):
    project = get_accessible_project(request.user, pk)
    if project.owner_id != request.user.id:
        messages.error(request, "Only the project owner can edit project details.")
        return redirect("project_detail", pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            broadcast_project(project.pk, "Project details updated.")
            messages.success(request, "Project updated.")
            return redirect("project_detail", pk=pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "workspace/form_page.html", {"form": form, "heading": "Edit project", "back_url": "project_detail", "back_pk": pk})

@login_required
def add_member(request, pk):
    project = get_accessible_project(request.user, pk)
    if request.method == "POST" and project.owner_id == request.user.id:
        username = request.POST.get("username", "").strip()
        member = User.objects.filter(username__iexact=username).first()
        if member:
            project.members.add(member)
            if member != request.user:
                Notification.objects.create(recipient=member, project=project, message=f"You were added to project: {project.name}")
            broadcast_project(project.pk, f"{username} was added to the project.")
            messages.success(request, f"{username} added to the team.")
        else:
            messages.error(request, "No user found with that username. Ask them to register first.")
    return redirect("project_detail", pk=pk)

@login_required
def task_create(request, pk):
    project = get_accessible_project(request.user, pk)
    if request.method == "POST":
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            if task.assignee and task.assignee != request.user:
                Notification.objects.create(recipient=task.assignee, project=project, message=f"New task assigned to you: {task.title}")
            broadcast_project(project.pk, f"New task created: {task.title}")
            messages.success(request, "Task created.")
            return redirect("project_detail", pk=pk)
    else:
        form = TaskForm(project=project)
    return render(request, "workspace/form_page.html", {"form": form, "heading": "Create a task", "back_url": "project_detail", "back_pk": pk})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task.objects.select_related("project", "assignee", "created_by"), pk=pk)
    project = get_accessible_project(request.user, task.project_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            for member in project.members.exclude(pk=request.user.pk):
                Notification.objects.create(recipient=member, project=project, message=f"New comment on task: {task.title}")
            if project.owner_id != request.user.id and project.owner_id not in project.members.values_list("id", flat=True):
                Notification.objects.create(recipient=project.owner, project=project, message=f"New comment on task: {task.title}")
            broadcast_project(project.pk, f"New comment on {task.title}")
            messages.success(request, "Comment added.")
            return redirect("task_detail", pk=pk)
    else:
        form = CommentForm()
    return render(request, "workspace/task_detail.html", {"task": task, "form": form, "project": project})

@login_required
@require_POST
def task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project = get_accessible_project(request.user, task.project_id)
    status = request.POST.get("status")
    if status in dict(Task.STATUS_CHOICES):
        task.status = status
        task.save(update_fields=["status"])
        broadcast_project(project.pk, f"{task.title} moved to {task.get_status_display()}.")
        messages.success(request, "Task status updated.")
    return redirect("project_detail", pk=project.pk)


@login_required
@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project = get_accessible_project(request.user, task.project_id)

    if request.user.id not in [project.owner_id, task.created_by_id]:
        messages.error(request, "You don't have permission to delete this task.")
        return redirect("project_detail", pk=project.pk)

    task_title = task.title
    project_id = project.pk
    task.delete()

    broadcast_project(project_id, f"Task deleted: {task_title}")
    messages.success(request, "Task deleted successfully.")

    return redirect("project_detail", pk=project_id)

def notifications(request):
    items = Notification.objects.filter(recipient=request.user)
    items.filter(is_read=False).update(is_read=True)
    return render(request, "workspace/notifications.html", {"items": items})

@login_required
def profile(request):
    return render(request, "workspace/profile.html")
