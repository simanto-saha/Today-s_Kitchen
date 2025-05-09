from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MealRegisterForm
from .models import Item, MealRegistration
from notification.models import Notification  # 👈 Make sure this is imported!
from django.contrib.auth.decorators import login_required

@login_required
def mealfunction(request):
    if request.method == 'POST':
        form = MealRegisterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['agree_terms']:
                # Create the meal registration
                registration = MealRegistration.objects.create(
                    user=request.user,
                    address=form.cleaned_data['address'],
                    start_date=form.cleaned_data['start_date'],
                    advance_payment=form.cleaned_data['advance_payment'],
                    meal_range=form.cleaned_data['meal_range']
                )

                # 🛎️ Create notification for meal registration
                Notification.objects.create(
                    title='Meal Registration Successful',
                    message=f'Hi {request.user.username}, your meal registration for range {registration.meal_range} has been successfully recorded.',
                )

                return redirect('main-home')
            
            else:
                form.add_error('agree_terms', 'You must agree to the terms and policies.')
    else:
        form = MealRegisterForm()

    return render(request, 'meal/meal_regestration.html', {'form': form})
    