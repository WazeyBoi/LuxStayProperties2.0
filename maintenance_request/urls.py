from django.urls import path
from . import views

app_name = 'maintenance_request'

urlpatterns = [
    path('', views.maintenance_request_list, name='maintenance_request_list'),
    path('create/<int:propertyid>/<int:tenantid>/', views.maintenance_request_create, name='maintenance_request_create'),
    path('owner-requests/', views.owner_maintenance_requests, name='maintenance_request_ownerlist'),
    path('accept/<int:requestid>/', views.accept_maintenance_request, name='accept_request'),
    path('complete/<int:requestid>/', views.complete_maintenance_request, name='complete_request'),
]
