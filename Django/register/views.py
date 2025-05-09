from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm, UserProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .models import Category, MenuItem, RestaurantName
from django.db.models import Q 


 
User = get_user_model()

def search_restaurants(request):
    query = request.GET.get('search', '')
    
    if query:
        restaurants = RestaurantName.objects.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query)
        )
    else:
        restaurants = RestaurantName.objects.all()
    
    context = {
        'restaurants': restaurants,
        'query': query
    }
    
    return render(request, 'register/search_result.html', context)

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
            user = authenticate(request, username=username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            login(request, user)
            return redirect('main-home')
        else:
            messages.error(request, "Invalid email or password")
    
    return render(request, 'register/login.html')

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
        
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            
           
            username = user.first_name or user.email.split('@')[0]
            user.username = username 
            user.save()
            messages.success(request, "Your account has been created! You can now login")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "register/register.html", {"form": form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("main-home")  # or wherever you want to redirect after logout
    return redirect("main-home")


def edit_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit your profile")
        return redirect("login")
        
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully")
            return redirect("main-home")
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, "register/edit_profile.html", {"form": form})

def menu_view(request):
    restaurant_id = request.GET.get('restaurant')
    active_category = request.GET.get('category', 'All')
    
    restaurants = RestaurantName.objects.all()
    
    if restaurant_id and restaurant_id.isdigit():
        restaurant = get_object_or_404(RestaurantName, id=restaurant_id)
        categories = Category.objects.filter(restaurant=restaurant)
        menu_items = MenuItem.objects.filter(
            restaurant=restaurant,
            is_available=True
        )
        
        todays_specials = MenuItem.objects.filter(
            restaurant=restaurant,
            is_available=True,
            is_todays_special=True
        )
    else:
        restaurant = None
        categories = Category.objects.all()
        menu_items = MenuItem.objects.filter(is_available=True)
        
        todays_specials = MenuItem.objects.filter(
            is_available=True,
            is_todays_special=True
        )
    
    
    if active_category != 'All' and active_category.isdigit():
        menu_items = menu_items.filter(category_id=active_category)
    
    context = {
        'active_category': active_category,
        'categories': categories,
        'menu_items': menu_items,
        'restaurant': restaurant,
        'restaurants': restaurants,
        'todays_specials': todays_specials,
    }
    
    return render(request, 'register/menu.html', context)


def special_view(request):
    """View for displaying special menu items."""
    restaurant_id = request.GET.get('restaurant')
    
    
    if restaurant_id and restaurant_id.isdigit():
        restaurant = get_object_or_404(RestaurantName, id=restaurant_id)
        specials = MenuItem.objects.filter(
            restaurant=restaurant,
            is_available=True,
            is_todays_special=True
        )
    else:
        restaurant = None
        specials = MenuItem.objects.filter(
            is_available=True,
            is_todays_special=True
        )
    
    
    restaurants = RestaurantName.objects.all()
    
    context = {
        'specials': specials,
        'restaurant': restaurant,
        'restaurants': restaurants,
    }
    
    return render(request, "register/special.html", context)


def menu_item_detail(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    if menu_item.restaurant:
        related_items = MenuItem.objects.filter(
            restaurant=menu_item.restaurant,
            is_available=True
        ).exclude(id=item_id)[:4]  # Limit to 4 related items
        
        # Get today's special items from this restaurant
        todays_specials = MenuItem.objects.filter(
            restaurant=menu_item.restaurant,
            is_available=True,
            is_todays_special=True
        ).exclude(id=item_id)[:4]
    else:
        related_items = MenuItem.objects.filter(
            is_available=True
        ).exclude(id=item_id)[:4]
        
        # Get all today's special items
        todays_specials = MenuItem.objects.filter(
            is_available=True,
            is_todays_special=True
        ).exclude(id=item_id)[:4]
    
    context = {
        'item': menu_item,
        'related_items': related_items,
        'todays_specials': todays_specials,
    }
    
    return render(request, 'register/menu_item_detail.html', context)




