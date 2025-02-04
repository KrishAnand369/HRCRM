from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Client,Project


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
    if not request.user.is_superuser:
        projects = projects.filter(assigned_users=profile)
        
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
