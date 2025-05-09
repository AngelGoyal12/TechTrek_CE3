from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import JobApplication
from .forms import JobApplicationForm

def careers_view(request):
    """View for the careers page"""
    return render(request, 'careers/careers.html')

def submit_application(request):
    """Handle job application submissions"""
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect(reverse('careers:careers') + '#open-positions')
        else:
            messages.error(request, "There was an error with your submission. Please check the form and try again.")
            
    return redirect('careers:careers')