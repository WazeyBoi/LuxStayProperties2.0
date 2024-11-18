from django.urls import include, path
from . import views

app_name = 'maintenance_request'

urlpatterns = [
    # ... other URL patterns
    path('', include([
        path('', views.maintenance_request_list, name='maintenance_request_list'),
        path('form/<int:leaseid>/<int:tenantid>/', views.maintenance_request_create, name='maintenance_request_create'),
    ])),
]
