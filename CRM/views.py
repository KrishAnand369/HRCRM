
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile,Project,Client,User
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
    return render(request,"app/webkit/user/user-profilepage.html",context)



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
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic and profile_pic.content_type not in ['image/jpeg', 'image/png']:
            return render(request, 'app/webkit/user/user-edit-profile.html', {
                'error': 'Invalid file type. Only JPEG and PNG are allowed.',
            })
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
        'profile': profile, 'skills': skills, 'education': education
    })
 
 
def client_register(request):
    if request.method == 'POST':
        username = request.POST.get('clientName')
        email = request.POST.get('clientemail')
        password = request.POST.get('clientPassword')
        company_name = request.POST.get('companyName')
        contact_number = request.POST.get('contactNumber')
        address = request.POST.get('address')
        company_logo = request.FILES.get('client_logo')
        if company_logo and company_logo.content_type not in ['image/jpeg', 'image/png']:
            return render(request, 'app/webkit/client/clientlist.html', {
                'error': 'Invalid file type. Only JPEG and PNG are allowed.',
            })
        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create Client Profile
        Client.objects.create(user=user, company_name=company_name,company_logo=company_logo, contact_number=contact_number,address=address)

        messages.success(request, "Client registered successfully!")
        return redirect('CRM:clientList')

    return render(request, 'app/webkit/client/clientlist.html')

@login_required
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'app/webkit/client/clientlist.html',{ 'clients': clients })  


def new_project_view(request):
    if request.method == 'POST':
        name = request.POST.get('projectName')
        dueDate = request.POST.get('dueDate')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        client_id = request.POST.get('client')
        project = Project.objects.create(
            name=name,
            due_date=dueDate,
            description = description,
            priority = priority,
            status = status,
            client_id = client_id,
        )
        assigned_users = request.POST.getlist('assignMembers')
        project.save()
        project.assigned_users.set(assigned_users)
        
        return redirect('CRM:project')  # Replace with your actual redirect
    else:
        form = ProjectForm()
    users = UserProfile.objects.all()  # Fetch all users
    clients = Client.objects.all()  # Fetch all users
    return render(request, 'app/webkit/project/projects.html', {'form': form, 'users': users, 'clients':clients,})


def project_list(request):
    status = request.GET.get('status')  # Get the selected status
    users = UserProfile.objects.all()
    clients = Client.objects.all()  # Fetch all clients
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
        'clients':clients,
    }
    return render(request, 'app/webkit/project/projects.html', context)


















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


