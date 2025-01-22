from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, blank=False, null=False)
    phone = models.CharField(max_length=15, blank=False, null=False)
    country = models.CharField(max_length=15, blank=False, null=False)
    about = models.TextField()

class Skill(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='skills', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    proficiency = models.IntegerField()

class Education(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField()


# Team Model
class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(UserProfile, related_name="teams")
    leader = models.ForeignKey(UserProfile, related_name="led_teams", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


    


# Project Model
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")])
    status = models.CharField(max_length=15, choices=[("New", "New"), ("In Progress", "In Progress"), ("Completed", "Completed")])
    teams = models.ManyToManyField(Team, related_name="projects")
    assigned_users = models.ManyToManyField(UserProfile, related_name="assigned_projects", blank=True)

    def __str__(self):
        return self.name

# Task Model
class Task(models.Model):
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")])
    status = models.CharField(max_length=15, choices=[("New", "New"), ("In Progress", "In Progress"), ("Completed", "Completed")])
    assigned_to = models.ForeignKey(UserProfile, related_name="tasks", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"
