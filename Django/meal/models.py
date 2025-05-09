from django.db import models
from django.contrib.auth import get_user_model

# Correctly call get_user_model() to get the User model class
User = get_user_model()

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class MealRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    start_date = models.DateField()
    advance_payment = models.DecimalField(max_digits=8, decimal_places=2)
    meal_range = models.CharField(
        max_length=20,
        choices=[('150-200', '150 - 200'),
                 ('500-600', '500 - 600'),
                 ('1000+', '1000+')],
        default='150-200'  # Default value if not selected
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} Meal Registration'


