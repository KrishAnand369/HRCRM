from django.urls import path
from . import views
from CRM.controller import authView

app_name ="CRM"
urlpatterns = [
    path('', views.landing,name='landing'),
    
    path('register/', authView.register, name='register'),
    path('login/',authView.loginPage,name='loginpage'),
    path('logout/',authView.logoutPage,name='logoutpage'),
    
    
    path('home',views.home,name='home'),
    
    path('profile',views.userprofile,name='userprofile'),
    path('saveprofile/',views.save_profile,name='save_profile'),
    
    path('projects',views.project_list,name='project'),
    path('project/new/', views.project_save, name='new_project'),  # Create new project
    path('project/edit/<int:project_id>/', views.project_save, name='edit_project'),
    
    path('clients',views.client_list,name='clientList'),
    path('client/register/', views.client_register, name='client_create'),
    path('client/register/<int:client_id>/', views.client_register, name='client_edit'),
    
    path('tasks',views.task_list,name='taskList'),
    #path('new-task/', views.task_register, name='new_task'),
]