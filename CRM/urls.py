from django.urls import path
from . import views
from CRM.controller import authView
from CRM.appViews import clientView,projectView,taskView,dashboardView,employeeView,leaveView,teamView,estimateView,ticketView,eventView


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
    
    path('staffs/',employeeView.employee_list,name='employees'),
    
    path('apply_leave/',leaveView.apply_leave,name='apply_leave'),
    path('leave_applications/',leaveView.apply_leave_list,name='apply_leave_list'),
    path('my_applications/',leaveView.my_applications,name='my_applications'),
    path('approve-leave/<int:leave_id>/', leaveView.approve_leave, name='approve_leave'),
    path('decline-leave/<int:leave_id>/', leaveView.decline_leave, name='decline_leave'),
    path('aadmin-commend-leave/<int:leave_id>/', leaveView.save_commend_leave, name='make_commend_leave'),
    
    path('team/create/', teamView.create_team, name='create_team'),
    path('team/list/', teamView.list_teams, name='list_team'),
    path('team/<int:team_id>/edit_team/', teamView.create_team, name='edit_team'),
    path('team/<int:team_id>/add_member/', teamView.add_member, name='add_member'),
    path('team/<int:team_id>/set_leader/', teamView.set_leader, name='set_leader'),
     
    path('estimates/', estimateView.estimate_list, name='estimates'),
    path('estimates/delete/<int:estimate_id>/', estimateView.delete_estimate, name='delete_estimate'),
    path('estimates/save/<int:estimate_id>/', estimateView.estimate_save, name='estimate_save'),
    path('estimates/save/', estimateView.estimate_save, name='estimate_save'),
     
    path('tickets/create/', ticketView.ticket_save, name='create_ticket'),
    path('tickets/<int:ticket_id>/edit/', ticketView.ticket_save, name='edit_ticket'),
    path('tickets', ticketView.ticket_list, name='ticket_list'),
    
    path('calendar/', eventView.calendar_view, name='calendar'),
    path('all_events/', eventView.all_events, name='all_events'),
    path('add_event/', eventView.add_event, name='add_event'),

]   