
from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile,Project,Client,User,Task,Checklist,Comment,Attachment
from CRM.controller import authView
from .projectForm import ProjectForm
from datetime import datetime
from django.contrib.auth import login, authenticate

def landing(request):
    return render(request,"app/webkit/index.html")


@login_required
def home(request):
    # //profile = UserProfile.objects.get(user=request.user)
    # {'profile': profile,}
    return render(request,"app/webkit/main.html")




@login_required
def userprofile(request):
    userRole = authView.get_user_role(request.user)
    profile = UserProfile.objects.get(user=request.user)
    skills = profile.skills.all()
    education = profile.education.all()

    context = {
        'userRole':userRole,
        'profile': profile,
        'skills': skills,
        'education': education,
    }
    return render(request,"app/webkit/user/user-profilepage.html",context)



@login_required
def save_profile(request):
    profile = UserProfile.objects.get(user=request.user)  # Fetch the logged-in user's profile
    
    userRole =authView.get_user_role(request.user)
    if request.method == 'POST':
        # Fetching basic info
        about = request.POST.get('about')
        profile.about = about
        role = request.POST.get('role')
        profile.role = role
        phone = request.POST.get('phone')
        profile.phone = phone
        country = request.POST.get('country')
        profile.country = country
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic and profile_pic.content_type not in ['image/jpeg', 'image/png']:
            return render(request, 'app/webkit/user/user-edit-profile.html', {
                'error': 'Invalid file type. Only JPEG and PNG are allowed.',
            })
        if profile_pic:
            profile.profile_pic = profile_pic
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
    return render(request, 'app/webkit/user/user-edit-profile.html', {
        'profile': profile, 'skills': skills, 'education': education,'userRole':userRole
    })

    profile = UserProfile.objects.get(user=request.user)
    projects =Project.objects.all()
    users = UserProfile.objects.all()
    project_selected=request.GET.get('project_selected')
    #print("project_selected:"+project_selected)
    print(project_selected)
    if project_selected == "All Tasks" or not project_selected:
        # If 'All projects' is selected or no status is provided
        print("project_selected: reached")
        tasks = Task.objects.all()
    elif project_selected:  # If a specific status is selected
        tasks = Task.objects.filter(project=project_selected)
    
    taskList= []
    for task in tasks:
        
        checklists=task.checklists.all()
        comments=task.comments.all()
        attachments=task.attachments.all()
        completed_items=task.checklists.filter(is_completed = True).count()
        taskList.append({
        'task':task,
        'checklists':checklists,
        'comments':comments,
        'attachments':attachments,
        'completed_items':completed_items,
        })
    return render(request,"app/webkit/task/tasks.html",{'profile': profile,'projects':projects,'users':users,'tasks':taskList})