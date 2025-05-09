from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.urls import reverse
from django.contrib import messages
from .models import CustomUser
from courseApp.models import Order
from django.shortcuts import get_object_or_404
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import views
@csrf_exempt
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            response = requests.post(
                'http://127.0.0.1:5000/api/register',
                json=data,  
                headers={'Content-Type': 'application/json'}
            )
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Failed to connect to API', 'details': str(e)}, status=500)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            response = requests.post(
                'http://127.0.0.1:5000/api/login',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Failed to connect to API', 'details': str(e)}, status=500)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.user_type = form.cleaned_data['user_type']
            user.save()
            
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "There was an error with your registration. Please check the form and try again.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_user_type = request.POST.get('user_type')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser and selected_user_type != 'admin':
                messages.warning(request, "You have administrative privileges. Please select 'Admin' login type.")
                return redirect('login')
            
            if not user.is_superuser and not user.is_staff and selected_user_type == 'admin':
                messages.error(request, "Access denied. You don't have admin privileges.")
                return redirect('login')
            
            if user.is_superuser and user.user_type != 'admin':
                user.user_type = 'admin'
                user.save()
            
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! You've successfully logged in.")

            return redirect('dashboard')

        else:
            messages.error(request, "Invalid username or password. Please try again.")
    return render(request, 'users/login.html')

@login_required
def dashboard(request):
    if request.user.is_admin():
        return admin_dashboard(request)
    else:
        return user_dashboard(request)

@login_required
def user_dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'users/dashboard.html', {
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'accepted_orders': orders.filter(status='accepted').count(),
        'recent_orders': orders[:5]
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        messages.warning(request, "Access denied. You don't have permission to view the admin dashboard.")
        return redirect('user_dashboard')
    
    from courseApp.models import Course, Order
    
    courses = Course.objects.all()
    user_orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'courses': courses,
        'user_orders': user_orders,
        'total_orders': user_orders.count(),
        'pending_orders': user_orders.filter(status='pending').count(),
        'accepted_orders': user_orders.filter(status='accepted').count(),
        'rejected_orders': user_orders.filter(status='rejected').count(),
    }
    
    return render(request, 'users/admin_dashboard.html', context)


@login_required
def profile_view(request):
    if request.user.is_admin():
        return redirect('admin_dashboard')
    else:
        return redirect('user_dashboard')


def user_logout(request):
    username = request.user.username
    logout(request)
    messages.success(request, f"You have been successfully logged out. Goodbye, {username}!")
    return redirect('login')

@login_required
def accept_order(request, order_id):
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('dashboard')
    
    order = get_object_or_404(Order, id=order_id)
    order.status = 'accepted'
    order.save()
    
    messages.success(request, f"Order #{order_id} has been accepted.")
    return redirect('admin_dashboard')

@login_required
def reject_order(request, order_id):
    if not request.user.is_admin():
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('dashboard')
    
    order = get_object_or_404(Order, id=order_id)
    order.status = 'rejected'
    order.save()
    
    messages.warning(request, f"Order #{order_id} has been rejected.")
    return redirect('admin_dashboard')