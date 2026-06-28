# Nexus — Mini Social Media Platform

## Overview
Nexus is a minimalist, responsive social media web application built with Django. It allows users to register, create posts, share images, follow other users, and interact through likes and comments in a personalized feed. The design focuses on a clean, dark-themed UI that emphasizes content and usability.

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
   git clone <repository-url>
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

3. **Install the dependencies:**
   ```bash
   pip install django pillow
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000/` in your browser.

## Project Structure
```text
core/
├── migrations/
├── templates/
│   └── core/
│       ├── edit_profile.html
│       ├── feed.html
│       ├── login.html
│       ├── profile.html
│       ├── register.html
│       └── users.html
├── templatetags/
│   ├── __init__.py
│   └── custom_filters.py
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── tests.py
├── urls.py
└── views.py
```

## Screenshots
See /screenshots folder

## Author
[Your Name] - [College Details]
