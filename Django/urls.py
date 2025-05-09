"""
URL configuration for trial project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from register.views import menu_item_detail,menu_view,search_restaurants,special_view,register,login_view,logout_view,edit_profile
from django.conf import settings
from django.conf.urls.static import static
from meal.views import mealfunction
from discount.views import apply_promo_code, validate_promo_code
from notification.views import notification_list, notification_detail
from track.views import track_order
from complain.views import complaint_view

urlpatterns = [
    path('complain/',complaint_view, name='complain'),
    
    path('notifications/', notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/', notification_detail, name='notification_detail'),

    path('promo_code',apply_promo_code, name='promo'),
    path('validate_promo_code',validate_promo_code, name='validate_promo'),

    path('meal', mealfunction, name='meal'),

    path('track', track_order, name='track'),

    path('cart/', include('cart.urls')),

    path('menu/', menu_view, name='menu'),
    path('menu/item/<int:item_id>/', menu_item_detail, name='menu_item_detail'),
    path('special_menu', special_view, name='special-manu'),
    path('search/', search_restaurants, name='search_restaurants'),

    path('admin/', admin.site.urls),
    path('', include('user.urls')),
    path('register/',register, name='register'),
    path('login/',login_view, name='login'),
    path('logout/',logout_view, name='logout'),
    path('edit_profile/',edit_profile, name='edit-profile'),
    
    
    
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='register/password_reset.html'), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='register/password_reset_done.html'), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', #UIDb64 is the User's ID encoded in base64 and the token is check that the password is valid
         auth_views.PasswordResetConfirmView.as_view(template_name='register/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='register/password_reset_complete.html'), 
         name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
