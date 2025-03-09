from django.urls import path
from . import views
from CRM.controller import authView
from CRM.appViews import clientView,projectView,taskView,dashboardView,employeeView

app_name ="CRM"
urlpatterns = [
    path('', views.landing,name='landing'),
    
    path('register/', authView.register, name='register'),
    path('adduser/', authView.createUser, name='createUser'),
    path('login/',authView.loginPage,name='loginpage'),
    path('logout/',authView.logoutPage,name='logoutpage'),
    
    path('dashboard',dashboardView.dashboard,name='userDashboard'),
    path('clock-in/', dashboardView.clock_in, name='clock_in'),
    path('clock-out/', dashboardView.clock_out, name='clock_out'),
    
    
    path('home',views.home,name='home'),
    path('profile',views.userprofile,name='userprofile'),
    path('saveprofile/',views.save_profile,name='save_profile'),
    
    path('projects',projectView.project_list,name='project'),
    path('project/new/', projectView.project_save, name='new_project'),  # Create new project
    path('project/edit/<int:project_id>/', projectView.project_save, name='edit_project'),
    
    path('clients',clientView.client_list,name='clientList'),
    path('client/register/', clientView.client_register, name='client_create'),
    path('client/register/<int:client_id>/', clientView.client_register, name='client_edit'),
    
    path('tasks',taskView.task_list,name='taskList'),
    path('new-task/', taskView.task_register, name='task_create'),
    path('update-task/<int:task_id>/', taskView.update_task, name="update_task"),
    
    path('staffs/',employeeView.employee_list,name='employees')
     
     
]