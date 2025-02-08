
from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile,Project,Client,User,Task,Checklist,Comment,Attachment
from .projectForm import ProjectForm
from datetime import datetime
from django.contrib.auth import login, authenticate

def landing(request):
    return render(request,"index.html")


@login_required
def home(request):
    # //profile = UserProfile.objects.get(user=request.user)
    # {'profile': profile,}
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


def task_register(request):
    print("ereached")
    if request.method == 'POST':
    
        # Get form data
        project_id = request.POST.get('project')
        title = request.POST.get('taskName')
        print(title)
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        priority = request.POST.get("priority")
        status = request.POST.get("status")
        checklist_items = request.POST.get('checklist', '').split(',')
        comments = request.POST.get('comments', '').split(',')
        print(comments)
        files = request.FILES.getlist('attachments')

        # Get project
        project = get_object_or_404(Project, id=project_id)

        # Create task
        task = Task(
            project=project,
            name=title,
            description=description,
            due_date=due_date,
            priority = priority,
            status = status
        )
        

        # Assign users
        assigned_to_id = request.POST.get("assignMembers")
        if assigned_to_id:
            task.assigned_to = get_object_or_404(UserProfile, id=assigned_to_id)
        else:
            task.assigned_to = None  # Unassign if no user is selected
        task.save()

        # Add checklist items
        for item in checklist_items:
            if item.strip():  # Ignore empty items
                Checklist.objects.create(task=task, item=item.strip())

        # Add comments
        for comment_text in comments:
            if comment_text.strip():  # Ignore empty comments
                Comment.objects.create(task=task, user=request.user, text=comment_text.strip())

        # Handle file uploads
        for file in files:
            Attachment.objects.create(task=task, file=file)

        return redirect('CRM:taskList')  # Redirect to task detail page
        # except Exception as e:
        #     # Handle errors (e.g., display an error message)
        #     return render(request, 'error.html', {'error_message': str(e)})
    else:
        # Render the form page for GET requests
        projects = Project.objects.all()
        users = UserProfile.objects.all()
        profile = UserProfile.objects.get(user=request.user)
        return render(request,"app/webkit/task/tasks.html",{'profile': profile,'projects':projects,'users':users})
        # return render(request, 'create_task.html', {'projects': projects, 'users': users})    
        
        
        
        
        
        
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        # Update Task Details
        task.name = request.POST.get("name")
        task.description = request.POST.get("description")
        task.due_date = request.POST.get("due_date")
        task.priority = request.POST.get("priority")
        task.status = request.POST.get("status")
        comments = request.POST.get('comments', '').split(',')
        files = request.FILES.getlist('attachments')
        checklist_items = request.POST.get('checklist_edit', '').split(',')
        

        # Update Assigned User
        assigned_to_id = request.POST.get("assigned_to")
        if assigned_to_id:
            task.assigned_to = get_object_or_404(UserProfile, id=assigned_to_id)
        else:
            task.assigned_to = None  # Unassign if no user is selected

        task.save()

        # Get all checklist items for this task
        all_checklists = Checklist.objects.filter(task=task)

        # Get the checklist IDs that were checked
        checked_items = request.POST.getlist("checklist_items")
        # Update checklist completion status
        for checklist in all_checklists:
            if task.status == "Completed" and len(all_checklists)== len(checked_items):
                checklist.is_completed = True
            else:    
                checklist.is_completed = str(checklist.id) in checked_items
            checklist.save()
            
        for comment_text in comments:
            if comment_text.strip():  # Ignore empty comments
                Comment.objects.create(task=task, user=request.user, text=comment_text.strip())
                
        for file in files:
            Attachment.objects.create(task=task, file=file)
            
        for item in checklist_items:
            if item.strip():  # Ignore empty items
                Checklist.objects.create(task=task, item=item.strip())
                
                
        #if check list filled then task completed 
        checkedItems= task.checklists.filter(is_completed = True)      
        if(len(Checklist.objects.filter(task=task))==len(checkedItems)):
            task.status = "Completed"
            print("reached completing task from check list")
            task.save()
        elif(len(checkedItems)==0):
            task.status = "New"
            print("reached completing task from check list2")
            task.save()
        else:
            task.status = "In Progress"
            print("reached completing task from check list3")
            task.save()
            
        
            
        return redirect('CRM:taskList')  # Redirect back to task page
    projects = Project.objects.all()
    users = UserProfile.objects.all()
    profile = UserProfile.objects.get(user=request.user)
    return render(request,"app/webkit/task/tasks.html",{'profile': profile,'projects':projects,'users':users})

@login_required
def task_list(request):
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