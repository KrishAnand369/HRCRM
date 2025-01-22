
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Skill, Education,Project
from .projectForm import ProjectForm
from datetime import datetime
from django.contrib.auth import login, authenticate

def landing(request):
    return render(request,"index.html")


@login_required
def home(request):
    return render(request,"app/webkit/main.html")




@login_required
def userprofile(request):
    profile = UserProfile.objects.get(user=request.user)
    skills = profile.skills.all()
    education = profile.education.all()

    context = {
        'profile': profile,
        'skills': skills,
        'education': education,
    }
    return render(request,"app/user-profilepage.html",context)



@login_required
def save_profile(request):
    profile = UserProfile.objects.get(user=request.user)  # Fetch the logged-in user's profile
    
    if request.method == 'POST':
        # Fetching basic info
        about = request.POST.get('about')
        
        
        about = request.POST.get('about')
        profile.about = about
        role = request.POST.get('role')
        profile.role = role
        phone = request.POST.get('phone')
        profile.phone = phone
        country = request.POST.get('country')
        profile.country = country
        profile.save()
        
        # Saving skills (only add new skills)
        skill_names = request.POST.getlist('skill_name[]')
        skill_proficiency = request.POST.getlist('skill_proficiency[]')

        profile.skills.all().delete()
        
         # Add new skills without deleting existing ones
        for name, proficiency in zip(skill_names, skill_proficiency):
            if name.strip():  # Avoid empty entries
                profile.skills.create(name=name, proficiency=proficiency)
            
        
        # Saving education (only add new education entries)
        institutions = request.POST.getlist('institution[]')
        courses = request.POST.getlist('course[]')
        start_years = request.POST.getlist('start_year[]')
        end_years = request.POST.getlist('end_year[]')
        
        profile.education.all().delete()

        # Add new education records without deleting existing ones
        for institution, course, start_year, end_year in zip(institutions, courses, start_years, end_years):
            profile.education.get_or_create(
                institution=institution, 
                course=course, 
                start_year=start_year, 
                end_year=end_year
            )

        messages.success(request, "Profile updated successfully!")
        return redirect('CRM:userprofile')

    skills = profile.skills.all()
    education = profile.education.all()
    return render(request, 'app/user-edit-profile.html', {
        'profile': profile, 'skills': skills, 'education': education
    })
    


def new_project_view(request):
    if request.method == 'POST':
        name = request.POST.get('projectName')
        dueDate = request.POST.get('dueDate')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        project = Project.objects.create(
            name=name,
            due_date=dueDate,
            description = description,
            priority = priority,
        )
        assigned_users = request.POST.getlist('assignMembers')
        project.save()
        project.assigned_users.set(assigned_users)
        
        return redirect('CRM:project')  # Replace with your actual redirect
    else:
        form = ProjectForm()
    users = UserProfile.objects.all()  # Fetch all users
    return render(request, 'app/webkit/projects.html', {'form': form, 'users': users})


def project(request):
    status = request.GET.get('status')  # Get the selected status
    users = UserProfile.objects.all()
    if status == 'All projects' or not status:  # If 'All projects' is selected or no status is provided
        projects = Project.objects.all()
    elif status:  # If a specific status is selected
        projects = Project.objects.filter(status=status)
        
    projects_with_completion = []
    for project in projects:
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(status='Completed').count()
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        projects_with_completion.append({
            'project': project,
            'completion_percentage': round(completion_percentage, 2),
        })

    context = {
        'projects': projects_with_completion,
        'status': status,
        'users': users,
    }
    return render(request, 'app/webkit/projects.html', context)


















# @login_required
# def userprofile1(request):
#     profile = UserProfile.objects.get(user=request.user)
#     skills = profile.skills.all()
#     education = profile.education.all()

#     context = {
#         'profile': profile,
#         'skills': skills,
#         'education': education,
#     }
#     return render(request,"app/webkit/user/profile.html",context)


