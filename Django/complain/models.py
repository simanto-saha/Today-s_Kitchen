from django.db import models

class Complaint(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)
    issue = models.TextField()
    order_number = models.CharField(max_length=50, blank=True, null=True)
    complaint_type = models.CharField(max_length=50, blank=True, null=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Complaint from {self.name} on {self.date.strftime('%Y-%m-%d')}"
