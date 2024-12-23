from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from leases.models import Lease
from users.models import User
from .models import Payment
from .forms import PaymentForm

@login_required
def payment_list(request):
    payments = Payment.objects.filter(tenantId=request.user)

    paginator = Paginator(payments, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'rent_payment/payment_list.html', {'page_obj': page_obj})

@login_required
def payment_create(request, leaseid, tenantid):
    lease = get_object_or_404(Lease, id=leaseid, tenant_id=tenantid)
    tenant = get_object_or_404(User, id=tenantid)

    # Get the remaining balance from the lease
    remaining_balance = lease.remaining_balance

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.leaseId = lease
            payment.tenantId = tenant

            # Get the payment amount
            payment_amount = payment.totalAmount

            # Check if the payment amount exceeds the remaining balance
            if payment_amount > remaining_balance:
                form.add_error('totalAmount', f'Payment amount cannot exceed the remaining balance of {remaining_balance:.2f}.')
                return render(request, 'rent_payment/payment_form.html', {
                    'form': form,
                    'lease': lease,
                    'tenant': tenant,
                    'remaining_balance': remaining_balance
                })

            # Deduct the payment amount from the remaining balance
            remaining_balance -= payment_amount

            # Update lease fields
            if remaining_balance <= 0:
                lease.payment_status = 'paid'
                lease.remaining_balance = 0
                lease.status = 'active'
            else:
                lease.payment_status = 'partially_paid'
                lease.remaining_balance = remaining_balance
                lease.status = 'active'

            lease.save()
            payment.save()

            return redirect('pending_list')
    else:
        form = PaymentForm()

    return render(request, 'rent_payment/payment_form.html', {
        'form': form,
        'lease': lease,
        'tenant': tenant,
        'remaining_balance': remaining_balance
    })

@login_required
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


@login_required
def payment_delete(request, paymentId):
    payment = get_object_or_404(Payment, paymentId=paymentId)
    if request.method == "POST":
        payment.delete()
        return redirect('payment_list')
    return render(request, 'rent_payment/payment_confirm_delete.html', {'payment': payment})


@login_required
def pending_list(request):
    # Fetch leases based on payment status
    unpaid = Lease.objects.filter(tenant=request.user, payment_status='unpaid')
    partially_paid = Lease.objects.filter(tenant=request.user, payment_status='partially_paid')
    paid = Lease.objects.filter(tenant=request.user, payment_status='paid')

    # Paginator for unpaid, partially paid, and paid leases
    unpaid_paginator = Paginator(unpaid, 5)
    partially_paid_paginator = Paginator(partially_paid, 5)
    paid_paginator = Paginator(paid, 5)

    unpaid_page_number = request.GET.get('unpaid_page')
    partially_paid_page_number = request.GET.get('partially_paid_page')
    paid_page_number = request.GET.get('paid_page')

    try:
        unpaid_page_obj = unpaid_paginator.get_page(unpaid_page_number)
    except PageNotAnInteger:
        unpaid_page_obj = unpaid_paginator.page(1)
    except EmptyPage:
        unpaid_page_obj = unpaid_paginator.page(unpaid_paginator.num_pages)

    try:
        partially_paid_page_obj = partially_paid_paginator.get_page(partially_paid_page_number)
    except PageNotAnInteger:
        partially_paid_page_obj = partially_paid_paginator.page(1)
    except EmptyPage:
        partially_paid_page_obj = partially_paid_paginator.page(partially_paid_paginator.num_pages)

    try:
        paid_page_obj = paid_paginator.get_page(paid_page_number)
    except PageNotAnInteger:
        paid_page_obj = paid_paginator.page(1)
    except EmptyPage:
        paid_page_obj = paid_paginator.page(paid_paginator.num_pages)

    # Add prices to unpaid leases
    for lease in unpaid_page_obj:
        lease.price = lease.remaining_balance
    for lease in partially_paid_page_obj:
        lease.price = lease.remaining_balance
    for lease in paid_page_obj:
        lease.price = lease.remaining_balance

    return render(request, 'rent_payment/pending_list.html', {
        'unpaid_page_obj': unpaid_page_obj,
        'partially_paid_page_obj': partially_paid_page_obj,
        'paid_page_obj': paid_page_obj
    })



@login_required
def payment_list_propertyowner(request):
    if request.user.role != 'property_owner':
        return redirect('home')  # Restrict access to property owners only

    # Filter leases where the property belongs to the logged-in property owner
    leases = Lease.objects.filter(property__owner=request.user)
    properties_with_payments = []

    # Gather payment details for properties owned by the property owner
    for lease in leases:
        payments = Payment.objects.filter(leaseId=lease)
        for payment in payments:
            properties_with_payments.append({
                'property_name': lease.property.property_name,
                'property_id': lease.property.id,
                'tenant_first_name': lease.tenant.first_name,  # Include tenant's first name
                'amount_paid': payment.totalAmount,
                'payment_date': payment.paymentDate,
            })

    # Paginate the payments
    paginator = Paginator(properties_with_payments, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'rent_payment/payment_list_propertyowner.html', {'page_obj': page_obj})

@login_required
def payment_history(request):
    # Fetch all payments made by the current tenant
    payments = Payment.objects.filter(tenantId=request.user).order_by('-paymentDate')  # Order by most recent payments

    # Paginate the payment history
    paginator = Paginator(payments, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Render the template with paginated payment history
    return render(request, 'rent_payment/payment_history.html', {'page_obj': page_obj})