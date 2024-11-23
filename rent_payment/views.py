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
    # Get the lease and tenant
    lease = get_object_or_404(Lease, id=leaseid, tenant_id=tenantid)
    tenant = get_object_or_404(User, id=tenantid)

    # Get the price from the associated property
    property_price = lease.property.price

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            
            # Validate the totalAmount matches the property price
            if payment.totalAmount != property_price:
                form.add_error('totalAmount', 'Total amount must match the property price.')
            else:
                # Save payment details
                payment.leaseId = lease
                payment.tenantId = tenant
                payment.save()

                # Update lease status
                lease.status = 'active'
                lease.payment_status = 'paid'
                lease.save()

                return redirect('pending_list')
    else:
        # Pre-fill the form with the price and current date
        form = PaymentForm(initial={
            'totalAmount': property_price
        })

    return render(request, 'rent_payment/payment_form.html', {
        'form': form,
        'lease': lease,
        'tenant': tenant
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
    unpaid = Lease.objects.filter(tenant=request.user, payment_status='unpaid')
    paid = Lease.objects.filter(tenant=request.user, payment_status='paid')

    unpaid_paginator = Paginator(unpaid, 5)
    paid_paginator = Paginator(paid, 5)

    unpaid_page_number = request.GET.get('unpaid_page')
    paid_page_number = request.GET.get('paid_page')

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

    # Add prices to unpaid leases
    for lease in unpaid_page_obj:
        lease.price = lease.property.price

    return render(request, 'rent_payment/pending_list.html', {
        'unpaid_page_obj': unpaid_page_obj,
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
                'amount_paid': payment.totalAmount,
                'payment_date': payment.paymentDate,
            })

    # Paginate the payments
    paginator = Paginator(properties_with_payments, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'rent_payment/payment_list_propertyowner.html', {'page_obj': page_obj})
