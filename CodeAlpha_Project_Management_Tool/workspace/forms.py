from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Project, Task, Comment

User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "deadline"]
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"})}

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assignee", "priority", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields["assignee"].queryset = (project.members.all() | User.objects.filter(pk=project.owner_id)).distinct()
        self.fields["assignee"].required = False

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Share an update or ask a question..."})}
