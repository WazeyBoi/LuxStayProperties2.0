from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_list, name='feedback_list'),
     path('create/<int:leaseid>/<int:tenantid>/', views.feedback_create, name='feedback_create'),
    path('owner/', views.feedback_ownerlist, name='feedback_ownerlist'),
    path('mark_as_viewed/<int:feedbackId>/', views.mark_feedback_as_viewed, name='mark_as_viewed'),

]
