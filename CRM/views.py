
from django.shortcuts import render,get_object_or_404, redirect
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
    profile = UserProfile.objects.get(user=request.user)
    return render(request,"app/webkit/main.html",{'profile': profile,})




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
 
 
def client_register(request, client_id=None):
    if request.method == 'POST':
        profile = UserProfile.objects.get(user=request.user)
        username = request.POST.get('clientName')
        email = request.POST.get('clientemail')
        password = request.POST.get('clientPassword')
        company_name = request.POST.get('companyName')
        contact_number = request.POST.get('contactNumber')
        address = request.POST.get('address')
        company_logo = request.FILES.get('client_logo')

        if company_logo and company_logo.content_type not in ['image/jpeg', 'image/png']:
            messages.error(request, 'Invalid file type. Only JPEG and PNG are allowed.')
            return redirect('CRM:clientList')

        if client_id:
            # Update existing client
            client = get_object_or_404(Client, id=client_id)
            client.company_name = company_name
            client.contact_number = contact_number
            client.address = address
            if company_logo:
                client.company_logo = company_logo
            client.user.username = username
            client.user.email = email
            if password:
                client.user.set_password(password)  # Only update password if provided
            client.user.save()
            client.save()
            messages.success(request, "Client updated successfully!")
        else:
            # Create new client
            user = User.objects.create_user(username=username, email=email, password=password)
            Client.objects.create(user=user, company_name=company_name, company_logo=company_logo, contact_number=contact_number, address=address)
            messages.success(request, "Client registered successfully!")

        return redirect('CRM:clientList')

    client = None
    if client_id:
        client = get_object_or_404(Client, id=client_id)

    return render(request, 'app/webkit/client/clientlist.html', {'client': client,'profile':profile})

@login_required
def client_list(request):
    clients = Client.objects.all()
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'app/webkit/client/clientlist.html',{'profile': profile, 'clients': clients })  


@login_required
def project_list(request):
    profile = UserProfile.objects.get(user=request.user)
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
        'profile': profile,
    }
    return render(request, 'app/webkit/project/projects.html', context)

@login_required
def task_list(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request,"app/webkit/task/tasks.html",{'profile': profile,})







def project_save(request, project_id=None):
    project = None
    if project_id:  # Edit existing project
        project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        name = request.POST.get('projectName')
        due_date = request.POST.get('dueDate')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        client_id = request.POST.get('client')
        assigned_users = request.POST.getlist('assignMembers')

        if project:  # Update existing project
            project.name = name
            project.due_date = due_date
            project.description = description
            project.priority = priority
            project.status = status
            project.client_id = client_id
            project.assigned_users.set(assigned_users)
            project.save()
        else:  # Create new project
            project = Project.objects.create(
                name=name,
                due_date=due_date,
                description=description,
                priority=priority,
                status=status,
                client_id=client_id,
            )
            project.assigned_users.set(assigned_users)

        return redirect('CRM:project')
    profile = UserProfile.objects.get(user=request.user)
    
    users = UserProfile.objects.all()
    clients = Client.objects.all()
    return render(request, 'app/webkit/project/projects.html', {
        'users': users, 'clients': clients, 'profile': profile, 'project': project
    })








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


