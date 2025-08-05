# HRCRM

## Overview
HRCRM is a comprehensive Human Resources and Customer Relationship Management system built with Django. It streamlines employee management, client interactions, project tracking, attendance, and invoicing for organizations of all sizes.

## Features
- Employee and client management
- Project and task tracking
- Attendance and clock-in/clock-out system
- Leave and event management
- Invoicing and salary slip generation
- Role-based dashboards (Admin, Employee, Client)
- File uploads and document management
- Notifications and reporting

## Technologies Used
- Python 3
- Django
- SQLite (default, can be replaced)
- HTML, CSS, JavaScript (for frontend)

## Getting Started
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd HRCRM
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
4. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```
5. **Run the development server:**
   ```bash
   python manage.py runserver 8011
   ```
6. **Access the app:**
   Visit `http://127.0.0.1:8011/` in your browser.

## Usage
- Log in as admin, employee, or client to access respective dashboards.
- Manage projects, tasks, attendance, and invoices from the web interface.
- Upload documents and view reports as needed.

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

