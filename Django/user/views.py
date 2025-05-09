from django.shortcuts import render

def home(request):
    return render(request, 'user/base.html')

def main(request):
    return render(request, 'user/main.html')

def about(request):
    return render(request, 'user/about.html')
