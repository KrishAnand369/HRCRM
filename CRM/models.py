from django.db import models
from django.contrib.auth.models import User
import datetime
from datetime import timedelta, date,time
import os
from django.utils import timezone


def get_file_path (request,filename):
    original_filename = filename
    nowTime = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename="%s%s" %(nowTime,original_filename)
    return os.path.join('uploads/',filename)
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=255)
    company_logo = models.ImageField(upload_to=get_file_path, null=False, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)  # Add client-specific fields

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile")
    profile_pic = models.ImageField(upload_to=get_file_path, null=False, blank=True)
    role = models.CharField(max_length=15, blank=False, null=False)
    phone = models.CharField(max_length=15, blank=False, null=False)
    country = models.CharField(max_length=15, blank=False, null=False)
    about = models.TextField()

    def __str__(self):
        return self.user.username

    def is_clocked_in(self):
        """
        Check if the user is currently clocked in.
        """
        last_event = self.clock_events.order_by('-timestamp').first()
        return last_event is not None and last_event.event_type == 'IN'

    def daily_hours_worked(self):
        """
        Calculate the total hours the user worked on a specific date.
        """
        date = timezone.now().date()
        
        events = self.clock_events.filter(date=date).order_by('timestamp')

        total_time = timedelta()
        clock_in_time = None

        for event in events:
            if event.event_type == 'IN':
                clock_in_time = event.timestamp
            elif event.event_type == 'OUT' and clock_in_time is not None:
                total_time += event.timestamp - clock_in_time
                clock_in_time = None  # Reset for the next pair

        # Handle incomplete clock-out (e.g., user forgot to clock out)
        if clock_in_time is not None:
            current_time = timezone.now()
            # Assume the user clocked out at the end of the workday (e.g., 5:00 PM)
            end_of_day = timezone.make_aware(timezone.datetime.combine(current_time.date(), time(20, 0)))  # 5:00 PM
            if current_time < end_of_day:
                end_of_day_naive = timezone.datetime.combine(date, timezone.datetime.min.time()) + timedelta(hours=12)
                end_of_day = timezone.make_aware(end_of_day_naive)
            # If current time is before 5:00 PM, calculate time up to the current time
                total_time += current_time - clock_in_time
            else:
                total_time += end_of_day - clock_in_time

        # Convert total_time to hours and minutes
        total_seconds = int(total_time.total_seconds())
        return total_seconds
        # hours = total_seconds // 3600
        # minutes = (total_seconds % 3600) // 60

        # # Format the time as "HH hrs: MM minutes"
        # return f"{hours:02d} hrs: {minutes:02d} minutes"

    def weekly_hours_worked(self):
        """
        Calculate the total hours the user worked in the current week (Monday to Friday).
        Also returns a daily breakdown of hours worked.
        """
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
        end_of_week = start_of_week + timedelta(days=4)  # Friday of the current week

        daily_hours = {}
        total_weekly_hours = 0

        for day in range(5):  # Monday to Friday
            current_day = start_of_week + timedelta(days=day)
            hours_worked = self.daily_hours_worked(current_day)
            daily_hours[current_day] = hours_worked
            total_weekly_hours += hours_worked

        return round(total_weekly_hours, 2)
        

class Skill(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='skills', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    proficiency = models.IntegerField()

class Education(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField()


# Team Model
class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(UserProfile, related_name="team")
    leader = models.ForeignKey(UserProfile, related_name="led_teams", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def is_leader(self, user):
        return self.leader == user

    def can_edit_team(self, user):
        return user.is_superuser or self.is_leader(user)

    def add_member(self, user, requesting_user):
        if self.can_edit_team(requesting_user):
            self.members.add(user)
            return True
        return False

    def set_leader(self, user, requesting_user):
        if self.can_edit_team(requesting_user) and user in self.members.all():
            self.leader = user
            self.save()
            return True
        return False



    


# Project Model
class Project(models.Model):
    client = models.ForeignKey(Client, related_name="projects", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")])
    status = models.CharField(max_length=15, choices=[("New", "New"), ("In Progress", "In Progress"), ("Completed", "Completed")])
    teams = models.ManyToManyField(Team, related_name="projects")
    assigned_users = models.ManyToManyField(UserProfile, related_name="assigned_projects", blank=True)

    def __str__(self):
        return self.name

# Task Model
class Task(models.Model):
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")])
    status = models.CharField(max_length=15, choices=[("New", "New"), ("In Progress", "In Progress"), ("Completed", "Completed")])
    assigned_to = models.ForeignKey(UserProfile, related_name="tasks", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"
    
class Checklist(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='checklists')
    item = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ClockEvent(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='clock_events')
    event_type = models.CharField(max_length=10, choices=[('IN', 'Clock In'), ('OUT', 'Clock Out')])
    timestamp = models.DateTimeField(default=timezone.now)  # Time of the event
    date = models.DateField(default=timezone.now)  # Date of the event

    def __str__(self):
        return f"{self.profile.user.username} - {self.event_type} - {self.timestamp}"

    class Meta:
        ordering = ['timestamp']  # Ensure events are ordered by time
        
class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='leave_applications')
    reason = models.TextField()
    date = models.DateField()
    documents = models.FileField(upload_to='leave_documents/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    to_admin = models.ForeignKey(UserProfile, related_name="leave_applys", on_delete=models.SET_NULL, null=True)
    admin_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.status}"

class Estimate(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_estimates')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='received_estimates')
    document = models.FileField(upload_to='estimates/%Y/%m/%d/')
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Estimate for {self.project.name} - {self.status}"
    
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Created','Created'),
        ('Assigned', 'Assigned'),
        ('Pending', 'Pending'),
        ('Solved', 'Solved'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_tickets')
    topic = models.CharField(max_length=200)
    description = models.TextField()
    assigned_employee = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Created')
    created_at = models.DateTimeField(auto_now_add=True)
    document = models.FileField(upload_to='tickets/%Y/%m/%d/')
        
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    is_global = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='personal_events')
    
    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return self.title

    @property
    def event_color(self):
        if self.is_global:
            return 'purple'
        return 'blue'
    
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.message}"
    
#salarySlip
class SalarySlip(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    slip_file = models.FileField(upload_to='salary_slips/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.month}"