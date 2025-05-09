from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet

router = DefaultRouter()
router.register(r'cart-items', CartItemViewSet)
urlpatterns = [
    
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('ai/', views.ai, name='ai'),
    path('accessibility/', views.accessibility, name='accessibility'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('cpp/', views.cpp, name='cpp'),
    path('datascience/', views.datascience, name='datascience'),
    path('js/', views.js, name='js'),
    path('privacy/', views.privacy, name='privacy'),
    path('python/', views.python, name='python'),
    path('react/', views.react, name='react'),
    path('sql/', views.sql, name='sql'),
    path('terms/', views.terms, name='terms'),
    path('webdev/', views.webdev, name='webdev'),
    path('cart/', views.cart, name='cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    # path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'), 
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('my-orders/', views.order_history, name='order_history'),
    path('add-course/', views.add_course, name='add_course'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin/course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('admin/course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('orders/<int:order_id>/accept/', views.accept_order, name='accept_order'),
    path('orders/<int:order_id>/reject/', views.reject_order, name='reject_order'),
    path('api/courses/create/', views.create_course, name='create_course'),
    path('api/courses/<int:course_id>/update/', views.update_course, name='update_course'),
    path('api/courses/<int:course_id>/delete/', views.delete_course_api, name='delete_course_api'),

    path('consume/', views.consume_flask_api, name='consume_flask_api'),
    path('registerapi/', views.register_user, name='register_user'),
    path('loginapi/', views.login_user, name='login_user'),
    path('courses/', views.get_courses, name='get_courses'),
    path('testimonials/', views.get_testimonials, name='get_testimonials'),
    path('contacts/', views.show_contacts, name='show_contacts'),
    path('showtestimonials/', views.show_testimonials, name='show_testimonials'),
    path('showcourses/', views.show_courses, name='show_courses'),
]