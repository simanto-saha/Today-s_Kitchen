## Today-s_Kitchen

A Django-based web application that allows restaurant kitchens to register, manage their profiles, and securely log in.  
All CSS and JavaScript are embedded directly within the HTML templates — no external static files required.

## Features

- ✅ Kitchen registration with specialties selection
- ✅ Secure password handling (hashed)
- ✅ Login and authentication system (shared login for customers & kitchens)
- ✅ User-friendly registration form with validation
- ✅ User can see if any special item for today
- ✅ All the menu are different section user can eachly find every kind of food  
- ✅ Django backend with SQLite (default) or other supported databases

## Tech Stack

- **Backend**: Django 5.x (or your version)
- **Database**: SQLite (default) or PostgreSQL/MySQL
- **Frontend**: Django Templates (HTML/CSS)

## Installation
Create a virtual environment

python -m venv env

source env/bin/activate   # On Windows: env\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py runserver

*[ all the html file are in one html folder ]*

Contact
📧 simanto.saha@g.bracu.ac.bd
