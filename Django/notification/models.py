from django.contrib.auth.models import User
from django.db import models
from cart.models import Order

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # null & blank True dilam
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, related_name='notifications', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


