# TaskFlow – Project Management Tool

A Django-based collaborative project and task management application.

## Features
- User registration, login and logout
- Create projects and add registered team members
- Create tasks, assign users, set priority and due dates
- Kanban-style To do / In progress / Completed board
- Task comments and activity notifications
- Real-time project broadcasts using Django Channels WebSockets
- SQLite database and responsive purple/navy dashboard

## Windows 10 setup

Open this folder in VS Code. In the integrated PowerShell terminal:

```powershell
py --version
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Open http://127.0.0.1:8000/dashboard/

## First use
1. Register two or more accounts in separate browser sessions (or use a second browser).
2. Sign in and create a project.
3. Add another registered username as a team member.
4. Create tasks and assign them to project members.
5. Open the same project in another browser session to test live updates.
6. Add comments and check the notification centre.

## Admin
Visit http://127.0.0.1:8000/admin/ and sign in with the superuser created above.

## Notes
- The included in-memory Channels layer is suitable for local development and demonstrations. It does not persist messages across server restarts and is not intended for multi-process production deployment.
- Before public deployment, set a strong environment-based SECRET_KEY, DEBUG=False, configure ALLOWED_HOSTS, HTTPS, static file hosting, and a production channel layer such as Redis.
- This is a functional starter MVP. It intentionally keeps project membership management simple: project owners can add registered users by username.
