from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MenuItem
from notification.models import Notification

@receiver(post_save, sender=MenuItem)
def create_notification_for_special_item(sender, instance, created, **kwargs):
    """
    Trigger a notification if the menu item is marked as special/popular etc.
    """
    special_labels = []
    if instance.is_todays_special:
        special_labels.append("Today's Special")
    if instance.is_chef_choice:
        special_labels.append("Chef's Choice")
    if instance.is_popular:
        special_labels.append("Popular Item")
    if instance.is_new:
        special_labels.append("New Item")

    # Only create notification if any special label is set
    if special_labels:
        title = f"New {', '.join(special_labels)}: {instance.name}"
        message = f"{instance.name} has been marked as {', '.join(special_labels)}! Check it out in the menu."

        Notification.objects.create(
            title=title,
            message=message,
            menu_item=instance
        )
