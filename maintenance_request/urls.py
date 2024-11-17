# maintenance_request/urls.py
from django.urls import path
from . import views



urlpatterns = [
    path('', views.maintenance_request_list, name='maintenance_request_list'),
    path('new/<int:leaseid>/<int:tenantid>/', views.maintenance_request_create, name='maintenance_request_create'),
]
