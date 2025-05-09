# meal/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MealRegistration
from notification.models import Notification

@receiver(post_save, sender=MealRegistration)
def create_notification_on_meal_registration(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,  # Use instance.user to get the user for the notification
            title='Meal Registration Successful',
            message=f'Hi {instance.user.username}, your meal registration for range {instance.meal_range} has been successfully recorded.',
        )
