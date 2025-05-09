from django import forms
from .models import Complaint



class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['name', 'email', 'issue', 'order_number', 'complaint_type']
        widgets = {
            'issue': forms.Textarea(attrs={'rows': 5}),
        }