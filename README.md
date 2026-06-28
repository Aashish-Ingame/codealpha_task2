# Nexus — Mini Social Media Platform

## Overview
Nexus is a lightweight, fully functional social media platform built with Django. It allows users to register, create profiles, share posts with images, and interact with others through likes, comments, and following/unfollowing mechanisms. It offers a personalized feed showcasing posts from followed users and provides an intuitive, dynamic interface.

## Features
- User registration and authentication
- Create posts with optional image upload
- Like and unlike posts
- Comment on posts
- Follow and unfollow users
- Personalized feed based on following
- User profiles with bio and avatar
- Browse and discover users

## Tech Stack
- Backend: Django (Python)
- Database: SQLite (development)
- Frontend: HTML, CSS, JavaScript (no frameworks)
- Media: Pillow for image handling

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd "Social Media App"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have `django` and `Pillow` installed if there is no `requirements.txt`: `pip install django Pillow`)*

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   The app will be accessible at `http://127.0.0.1:8000/`.

## Project Structure
```text
Social Media App/
├── core/                   # Main application directory
│   ├── migrations/         # Database migrations
│   ├── templates/          # HTML templates
│   ├── templatetags/       # Custom template tags
│   ├── admin.py            # Admin dashboard configuration
│   ├── forms.py            # Django forms for user input
│   ├── models.py           # Database models (User, Post, Comment, etc.)
│   ├── urls.py             # App-level URL routing
│   └── views.py            # View logic for handling requests
├── nexus/                  # Django project configuration directory
├── templates/              # Global HTML templates
├── manage.py               # Django command-line utility
└── db.sqlite3              # SQLite database file
```

## Screenshots
See `/screenshots` folder

## Author
[Your Name]
[Your College Details]
