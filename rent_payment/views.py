# rent_payment/views.py
from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect

from leases.models import Lease
from users.models import User
from .models import Payment
from .forms import PaymentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def payment_list(request):
    # Filter payments for the current user (tenant)
    payments = Payment.objects.filter(tenantId=request.user)  # Filtering payments by the logged-in user

    # Pagination: Show 5 payments per page
    paginator = Paginator(payments, 5)  # 5 items per page
    page_number = request.GET.get('page')  # Get the current page number from the request
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'rent_payment/payment_list.html', {'page_obj': page_obj})

def payment_create(request, leaseid, tenantid):
    lease = get_object_or_404(Lease, id=leaseid, tenant_id=tenantid)
    tenant = get_object_or_404(User, id=tenantid)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.leaseId = lease
            payment.tenantId = tenant
            payment.save()

            # Update lease status to 'paid' after successful payment
            lease.status  = 'active'
            lease.payment_status  = 'paid'
            lease.save()

            # Redirect to the Pending List (which should filter paid leases)
            return redirect('pending_list')  # Make sure 'pending_list' handles this filter

    else:
        form = PaymentForm()

    return render(request, 'rent_payment/payment_form.html', {
        'form': form,
        'lease': lease,
        'tenant': tenant
    })

def payment_update(request, paymentId):
    payment = get_object_or_404(Payment, paymentId=paymentId)
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('payment_list')
    else:
        form = PaymentForm(instance=payment)
    return render(request, 'rent_payment/payment_form.html', {'form': form})

def payment_delete(request, paymentId):
    payment = get_object_or_404(Payment, paymentId=paymentId)
    if request.method == "POST":
        payment.delete()
        return redirect('payment_list')
    return render(request, 'rent_payment/payment_confirm_delete.html', {'payment': payment})

def pending_list(request):
    # Filter leases based on payment_status and tenant's user status
    unpaid = Lease.objects.filter(tenant=request.user, payment_status='unpaid')
    paid = Lease.objects.filter(tenant=request.user, payment_status='paid')

    # Pagination: 5 items per page for unpaid and paid lists
    unpaid_paginator = Paginator(unpaid, 5)
    paid_paginator = Paginator(paid, 5)

    unpaid_page_number = request.GET.get('unpaid_page')  # Use a unique key for unpaid pagination
    paid_page_number = request.GET.get('paid_page')  # Use a unique key for paid pagination

    try:
        unpaid_page_obj = unpaid_paginator.get_page(unpaid_page_number)
    except PageNotAnInteger:
        unpaid_page_obj = unpaid_paginator.page(1)
    except EmptyPage:
        unpaid_page_obj = unpaid_paginator.page(unpaid_paginator.num_pages)

    try:
        paid_page_obj = paid_paginator.get_page(paid_page_number)
    except PageNotAnInteger:
        paid_page_obj = paid_paginator.page(1)
    except EmptyPage:
        paid_page_obj = paid_paginator.page(paid_paginator.num_pages)

    return render(request, 'rent_payment/pending_list.html', {
        'unpaid_page_obj': unpaid_page_obj,
        'paid_page_obj': paid_page_obj
    })
