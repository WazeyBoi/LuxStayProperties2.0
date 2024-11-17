# rent_payment/urls.py
from django.urls import path
from .views import payment_list, payment_create, payment_update, payment_delete, pending_list

urlpatterns = [
    path('payment-list', payment_list, name='payment_list'),
    path('create/<int:leaseid>/<int:tenantid>/', payment_create, name='payment_create'),
    path('update/<int:paymentId>/', payment_update, name='payment_update'),
    path('delete/<int:paymentId>/', payment_delete, name='payment_delete'),
    path('pending-list/', pending_list, name='pending_list'),
]
