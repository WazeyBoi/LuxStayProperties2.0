# feedback/urls.py
from django.urls import include, path
from . import views

app_name = 'feedback'

urlpatterns = [
    # ... other URL patterns
    path('', include([
        path('', views.feedback_list, name='feedback_list'),
        path('form/<int:leaseid>/<int:tenantid>/', views.feedback_create, name='feedback_create'),
    ])),
]
