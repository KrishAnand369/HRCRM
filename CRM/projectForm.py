from django import forms
from .models import Project
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'due_date', 'priority', 'status', 'teams', 'assigned_users']
