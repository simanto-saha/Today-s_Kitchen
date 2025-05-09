from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.urls import reverse

User = get_user_model()

class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="register_user_groups",  # Unique related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="register_user_permissions",  # Unique related_name
        related_query_name="user",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Remove if you don't need username

    def __str__(self):
        return self.email
    

class RestaurantName(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True)
    address = models.TextField()
    cuisine = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey(
        RestaurantName, 
        on_delete=models.CASCADE, 
        related_name='categories',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Tag(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    restaurant = models.ForeignKey(
        RestaurantName, 
        on_delete=models.CASCADE, 
        related_name='menu_items',
        null=True,
        blank=True
    )
    is_chef_choice = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_todays_special = models.BooleanField(default=False)  # Added field for today's special
    discount = models.PositiveIntegerField(null=True, blank=True)  # Optional discount for specials
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('menu_item_detail', args=[str(self.id)])    

