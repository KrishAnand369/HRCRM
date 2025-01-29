
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from CRM.models import Client, UserProfile,Project

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

def project_view(request, project_id=None):
    profile = UserProfile.objects.get(user=request.user)
    
    if project_id:  # Edit existing project
        project = get_object_or_404(Project, id=project_id)
    else:  # Create new project
        project = None

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

    users = UserProfile.objects.all()
    clients = Client.objects.all()
    return render(request, 'app/webkit/project/projects.html', {
        'users': users, 'clients': clients, 'profile': profile, 'project': project
    })




