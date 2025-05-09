from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from .models import Notification

def notification_list(request):
    notification = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notification/notification_list.html', {'notification': notification})

def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    # Optional: Mark notification as read
    notification.is_read = True
    notification.save()

    # Get the linked order (if any)
    order = notification.order

    context = {
        'notification': notification,
        'order': order,
    }

    return render(request, 'notification/notification_detail.html', context)