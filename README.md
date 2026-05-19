# Nexora

Nexora is a minimal social media app built with Django. Users can register, create posts with optional images, like posts, and comment in a global feed.

## Features
- User authentication (register, login, logout)
- Profiles with bio and optional avatar
- Posts with text and optional image
- Comments and likes
- Clean, responsive UI

## Tech Stack
- Django + SQLite
- HTML templates, CSS, and minimal JavaScript

## Setup
1. Create and activate a virtual environment.
2. Install dependencies.
3. Run migrations.
4. Start the server.

```powershell
python -m pip install django pillow
python manage.py migrate
python manage.py runserver
```

## Project Structure
- `users/` authentication and profiles
- `posts/` posts, comments, likes
- `templates/` HTML templates
- `static/` CSS and assets

## Usage
- Home feed: view all posts
- Create post: add a new post
- Profile: view and edit your profile

## Notes
- Image uploads are stored in `media/` in development.
