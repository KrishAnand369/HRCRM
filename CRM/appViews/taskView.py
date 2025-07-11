from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Task,Comment,Checklist,Attachment,Project,Client
from CRM.controller import authView
from CRM.utils import notify_user
from django.contrib import messages

@login_required
def task_register(request):
    if request.method == 'POST':
    
        # Get form data
        project_id = request.POST.get('project')
        title = request.POST.get('taskName')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        priority = request.POST.get("priority")
        status = request.POST.get("status")
        checklist_items = request.POST.get('checklist', '').split(',')
        comments = request.POST.get('comments', '').split(',')
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
            notify_user(task.assigned_to.user," You are assiged with a new Task: " + title)
        else:
            task.assigned_to = None  # Unassign if no user is selected
        task.save()

        # Add checklist items
        for item in checklist_items:
            if item.strip():  # Ignore empty items
                Checklist.objects.create(task=task, item=item.strip())
                if request.user != task.assigned_to.user:
                    notify_user(task.assigned_to.user," There is a new checkList items in Task: " + title + " from "+ request.user.username)

        # Add comments
        for comment_text in comments:
            if comment_text.strip():  # Ignore empty comments
                Comment.objects.create(task=task, user=request.user, text=comment_text.strip())
                if request.user != task.assigned_to.user:
                    notify_user(task.assigned_to.user," There is a new Comment in Task: " + title + " from "+ request.user.username)

        # Handle file uploads
        for file in files:
            Attachment.objects.create(task=task, file=file)
            if request.user != task.assigned_to.user:
                    notify_user(task.assigned_to.user," There is a new Attachment in Task: " + title + " from "+ request.user.username)

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
        
        
        
        
        
@login_required     
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        # Update Task Details
        if request.user.is_superuser:
            task.name = request.POST.get("name")
            task.description = request.POST.get("description")
            task.due_date = request.POST.get("due_date")
            task.priority = request.POST.get("priority")
            task.status = request.POST.get("status")
            checklist_items = request.POST.get('checklist_edit', '').split(',')
            for item in checklist_items:
                if item.strip():  # Ignore empty items
                    Checklist.objects.create(task=task, item=item.strip())
                    if request.user != task.assigned_to.user:
                        notify_user(task.assigned_to.user," There is a new checklist items in Task: " + task.name + " from "+ request.user.username)
                    
            # Update Assigned User
            assigned_to_id = request.POST.get("assigned_to")
            if assigned_to_id:
                task.assigned_to = get_object_or_404(UserProfile, id=assigned_to_id)
                notify_user(task.assigned_to.user," You are assiged with a new Task: " + task.name)
            else:
                task.assigned_to = None  # Unassign if no user is selected
                
        comments = request.POST.get('comments', '').split(',')
        files = request.FILES.getlist('attachments')
        
        

        

        task.save()
        if task.status == "Completed" :
            notify_user(task.project.client.user,"Task"+task.name+"is Completed")

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
                if request.user != task.assigned_to.user:
                    notify_user(task.assigned_to.user," There is a new Comment in Task: " + task.name + " from "+ request.user.username)
                
        for file in files:
            Attachment.objects.create(task=task, file=file)
            if request.user != task.assigned_to.user:
                    notify_user(task.assigned_to.user," There is a new Attachment in Task: " + task.name + " from "+ request.user.username)
            
        
                
                
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
    userRole = authView.get_user_role(request.user)
    projects =Project.objects.all()
    users = UserProfile.objects.all()
    project_selected=request.GET.get('project_selected')
    if project_selected == "All Tasks" or not project_selected:
        tasks = Task.objects.all()
    elif project_selected:  # If a specific status is selected
        tasks = Task.objects.filter(project=project_selected)
    if userRole == 'client':
        profile = Client.objects.get(user=request.user)
        projects = projects.filter(client=profile)
        tasks =Task.objects.filter(project__client=profile)
    else:
        profile = UserProfile.objects.get(user=request.user)
        if not request.user.is_superuser:
            tasks = tasks.filter(assigned_to=profile)
            projects = projects.filter(assigned_users=profile)
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
    return render(request,"app/webkit/task/tasks.html",{'userRole':userRole,'profile': profile,'projects':projects,'users':users,'tasks':taskList})

@login_required
def task_delete(request, task_id):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete task.")
        return redirect('CRM:taskList')
    task = get_object_or_404(Task, id=task_id)
    try:
        task.delete()
        messages.success(request, "Task deleted successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred while deleting the Task: {e}")
    return redirect('CRM:taskList')