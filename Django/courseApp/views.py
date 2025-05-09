from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect, get_object_or_404
from .models import CartItem
from .forms import ContactForm
from users.forms import CustomUserCreationForm
from .models import CartItem, Order, OrderItem, Course, Testimonial

import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CartItem
from .serializers import CartItemSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
def consume_flask_api(request):
    try:
        flask_url = f"{settings.FLASK_API_BASE_URL}/get_data"
        response = requests.get(flask_url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(data)
def get_courses_from_flask(request):
    try:
        response = requests.get('http://127.0.0.1:5000/courses')
        response.raise_for_status()
        courses = response.json()
        return JsonResponse({'courses': courses})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        response = requests.post('http://127.0.0.1:5000/api/registerapi', data=data)
        return JsonResponse(response.json(), status=response.status_code)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        response = requests.post('http://127.0.0.1:5000/api/loginapi', data=data)
        return JsonResponse(response.json(), status=response.status_code)
def get_courses(request):
    response = requests.get('http://127.0.0.1:5000/api/courses')
    return JsonResponse({'courses': response.json()})
@csrf_exempt
def create_course(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        response = requests.post("http://127.0.0.1:5000/api/courses", json=data)
        return JsonResponse(response.json(), status=response.status_code)
@csrf_exempt
def update_course(request, course_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        response = requests.put(f"http://127.0.0.1:5000/api/courses/{course_id}", json=data)
        return JsonResponse(response.json(), status=response.status_code)
@csrf_exempt
def delete_course_api(request, course_id):
    if request.method == 'DELETE':
        response = requests.delete(f"http://127.0.0.1:5000/api/courses/{course_id}")
        return JsonResponse(response.json(), status=response.status_code)

def get_testimonials(request):
    response = requests.get('http://127.0.0.1:5000/api/testimonials')
    return JsonResponse({'testimonials': response.json()})



def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at') if request.user.is_authenticated else Order.objects.none()
    return render(request, 'index.html', {'orders': orders})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            if user.user_type == 'admin':
                user.is_staff = True
                user.is_superuser = True
            user.save()
            login(request, user)
            return redirect('admin_dashboard' if user.is_admin() else 'user_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    next_page = request.GET.get('next', '')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_user_type = request.POST.get('user_type')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.user_type != selected_user_type:
                messages.error(request, f"You tried to login as {selected_user_type}, but your account is of type {user.user_type}.")
                return redirect('login')
            login(request, user)
            messages.success(request, "Login Successful!")
            
            
            if next_page:
                return redirect(next_page)
            return redirect('admin_dashboard' if user.user_type == 'admin' else 'user_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'users/login.html', {'next': next_page})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


class LoginRequiredMixin:
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return login_required(view)


def cart(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to view your cart.")
        return redirect(f"{reverse('login')}?next={reverse('cart')}")
    
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.price for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items, 
        'total': total, 
        'is_authenticated': True
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('index')
    courses = Course.objects.all()
    user_orders = Order.objects.filter(user__user_type='user')
    return render(request, 'admin_dashboard.html', {'courses': courses, 'user_orders': user_orders})


def index(request):
    return render(request, 'index.html')

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        plan_price = request.POST.get('plan_price')
        CartItem.objects.create(user=request.user, plan_type=plan_type, price=plan_price)
        messages.success(request, f"{plan_type} added to cart successfully!")
        return redirect('cart')
    return redirect('index')

@login_required
def remove_from_cart(request,item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id)
        item.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('cart')
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.price for item in cart_items)
    total = Decimal(str(total))
    tax = total * Decimal('0.18')
    grand_total = total + tax
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'tax': tax.quantize(Decimal('0.01')),
        'grand_total': grand_total.quantize(Decimal('0.01')),
        'is_authenticated': True
    })

@login_required
def process_payment(request):
    if request.method == 'POST':
        data = {key: request.POST.get(key) for key in ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zipcode']}
        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.price for item in cart_items)
        total = Decimal(str(total))
        tax = total * Decimal('0.18')
        grand_total = total + tax
        order = Order.objects.create(user=request.user, **data, total=total, tax=tax, grand_total=grand_total)
        for item in cart_items:
            OrderItem.objects.create(order=order, item_name=item.plan_type, price=item.price)
        cart_items.delete()
        messages.success(request, "Payment successful! Happy learning :)")
        return redirect('index')
    return redirect('checkout')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Add items before placing an order.")
        return redirect('cart')
    
    
    total = sum(item.price for item in cart_items)
    tax = total * Decimal('0.18')
    grand_total = total + tax
    
   
    order = Order.objects.create(
        user=request.user,
        first_name=request.user.first_name or "First",
        last_name=request.user.last_name or "Last",
        email=request.user.email or "email@example.com",
        phone="N/A",
        address="N/A",
        city="N/A",
        state="N/A",
        zipcode="000000",
        total=total,
        tax=round(tax, 2),
        grand_total=round(grand_total, 2)
    )
    
   
    for item in cart_items:
        OrderItem.objects.create(order=order, item_name=item.plan_type, price=item.price)
        item.delete()
    
    messages.success(request, "Your order has been placed successfully!")
    return redirect('order_history')


@csrf_exempt
@login_required
def add_course(request):
    if request.user.user_type != 'admin':
        return HttpResponseForbidden("Unauthorized access.")
    
    if request.method == 'POST':
        course_data = {
            'title': request.POST.get('title'),
            'instructor': request.POST.get('instructor'),
            'price': float(request.POST.get('price')),
            'description': request.POST.get('description'),
            'rating': 0.0,
            'rating_count': 0,
            'featured': False,
            'image_url': "/static/images/course-placeholder.jpg"
        }

        try:
            response = requests.post('http://127.0.0.1:5000/api/courses', json=course_data)
            if response.status_code == 201:
                messages.success(request, "Course created successfully (via Flask API).")
            else:
                messages.error(request, f"Failed to create course: {response.json().get('message')}")
        except Exception as e:
            messages.error(request, f"Error communicating with Flask API: {e}")

        return redirect('admin_dashboard')

    return render(request, 'course_form.html', {'action': 'Add'})

@csrf_exempt
@login_required
def edit_course(request, course_id):
    if request.user.user_type != 'admin':
        return HttpResponseForbidden("Unauthorized access.")
    
    if request.method == 'POST':
        updated_data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'instructor': request.POST.get('instructor'),
            'price': float(request.POST.get('price')),
            'rating': 0.0,
            'rating_count': 0,
            'featured': False,
            'image_url': "/static/images/course-placeholder.jpg"
        }

        try:
            response = requests.put(
                f'http://127.0.0.1:5000/api/courses/{course_id}',
                json=updated_data
            )
            if response.status_code == 200:
                messages.success(request, "Course updated via Flask API.")
            else:
                messages.error(request, f"Update failed: {response.json().get('message')}")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect('admin_dashboard')

    try:
        response = requests.get(f'http://127.0.0.1:5000/api/courses/{course_id}')
        if response.status_code == 200:
            course = response.json()
        else:
            messages.error(request, "Course not found in Flask.")
            return redirect('admin_dashboard')
    except Exception as e:
        messages.error(request, f"Error fetching course: {e}")
        return redirect('admin_dashboard')

    return render(request, 'course_form.html', {'course': course, 'action': 'Edit'})

@csrf_exempt
@login_required
def delete_course(request, course_id):
    if request.user.user_type != 'admin':
        return HttpResponseForbidden("Unauthorized access.")

    try:
        response = requests.delete(f'http://127.0.0.1:5000/api/courses/{course_id}')
        if response.status_code == 200:
            messages.success(request, "Course deleted via Flask API.")
        else:
            messages.error(request, f"Delete failed: {response.json().get('message')}")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect('admin_dashboard')


@require_POST
@user_passes_test(lambda u: u.is_staff)
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'accepted'
    order.save()
    messages.success(request, f"Order #{order_id} has been accepted.")
    return redirect('admin_dashboard')


@require_POST
@user_passes_test(lambda u: u.is_staff)
def reject_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'rejected'
    order.save()
    messages.warning(request, f"Order #{order_id} has been rejected.")
    return redirect('admin_dashboard')


@login_required
def user_dashboard(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'user_dashboard.html', {
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'accepted_orders': orders.filter(status='accepted').count(),
        'recent_orders': orders[:5]
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
            return redirect('contact')
        messages.error(request, 'There was an error with your submission. Please check the form.')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def is_admin(user):
    return user.is_authenticated and user.is_staff

def show_contacts(request):
    try:
        response = requests.get("http://127.0.0.1:5000/api/contacts")
        contacts = response.json() if response.status_code == 200 else []
    except Exception as e:
        contacts = []
        print("Error:", e)
    
    return render(request, 'contacts.html', {'contacts': contacts})

def show_testimonials(request):
    try:
        print("Fetching testimonials from Flask API...")
        response = requests.get('http://127.0.0.1:5000/api/testimonials')
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Response Data: {data}")
            
            if isinstance(data, dict) and 'testimonials' in data:
                testimonials = data['testimonials']
            else:
                testimonials = data
            
            print(f"Extracted testimonials: {testimonials}")
            
            formatted_testimonials = []
            for t in testimonials:
                formatted_testimonial = {
                    'content': t.get('content', ''),
                    'student_name': t.get('student_name', 'Anonymous'),
                    'student_title': t.get('student_title', 'Student'),
                    'image_url': t.get('image_url', '/static/images/placeholder.png')
                }
                formatted_testimonials.append(formatted_testimonial)
            
            print(f"Formatted testimonials: {formatted_testimonials}")
            return render(request, 'testimonials.html', {'testimonials': formatted_testimonials})
        else:
            print(f"API Error: Status code {response.status_code}")
            testimonials = []
            db_testimonials = Testimonial.objects.all()
            for t in db_testimonials:
                testimonials.append({
                    'content': t.message,
                    'student_name': t.name,
                    'student_title': 'Student',
                    'image_url': None
                })
            return render(request, 'testimonials.html', {'testimonials': testimonials})
    except Exception as e:
        print(f"Error fetching testimonials: {e}")
        testimonials = []
        db_testimonials = Testimonial.objects.all()
        for t in db_testimonials:
            testimonials.append({
                'content': t.message,
                'student_name': t.name,
                'student_title': 'Student',
                'image_url': None
            })
        return render(request, 'testimonials.html', {'testimonials': testimonials})
    
    
def show_courses(request):
    try:
        
        response = requests.get('http://127.0.0.1:5000/api/courses')
        if response.status_code == 200:
            courses_data = response.json()
            
            if isinstance(courses_data, dict) and 'courses' in courses_data:
                courses = courses_data['courses']
            else:
                courses = courses_data
            formatted_courses = []
            for c in courses:
                
                formatted_courses.append({
                    'title': c.get('title', 'Untitled Course'),
                    'description': c.get('description', 'No description available'),
                    'instructor': c.get('instructor', 'Staff'),
                    'price': c.get('price', '0.00'),
                })
            courses = formatted_courses
        else:
            
            courses = []
            db_courses = Course.objects.all()
            for c in db_courses:
                courses.append({
                    'title': c.title,
                    'description': c.description,
                    'instructor': c.instructor,
                    'price': c.price,
                })
    except Exception as e:
        print(f"Error fetching courses: {e}")
        
        courses = []
        db_courses = Course.objects.all()
        for c in db_courses:
            courses.append({
                'title': c.title,
                'description': c.description,
                'instructor': c.instructor,
                'price': c.price,
            })
        
    return render(request, 'courses.html', {'courses': courses})


def about(request): return render(request, 'about.html')
def ai(request): return render(request, 'ai.html')
def cpp(request): return render(request, 'cpp.html')
def datascience(request): return render(request, 'datascience.html')
def js(request): return render(request, 'js.html')
def accessibility(request): return render(request, 'accessibility.html')
def blog(request): return render(request, 'blog.html')
def privacy(request): return render(request, 'privacy.html')
def python(request): return render(request, 'python.html')
def react(request): return render(request, 'react.html')
def sql(request): return render(request, 'sql.html')
def terms(request): return render(request, 'terms.html')
def webdev(request): return render(request, 'webdev.html')