from django.shortcuts import render, redirect
from .forms import ComplaintForm
from notification.models import Notification

def complaint_view(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            form.save()  
            Notification.objects.create(
                user=request.user,
                message="Your complaint has been submitted successfully. A higher authority will get back to you soon.",
                is_read=False  # Initially, it's not read
            )
            return redirect('notification_list')
    else:
        form = ComplaintForm()
    return render(request, 'complain/complaint_form.html', {'form': form})
