from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='user-home'),
    path('main/',views.main, name='main-home'),
    path('about/',views.about, name='about'),
    
]