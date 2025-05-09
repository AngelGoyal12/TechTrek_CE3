from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
     path('', views.careers_view, name='careers'),
     path('apply/', views.submit_application, name='submit_application'),
]
