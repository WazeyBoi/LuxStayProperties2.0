# rent_payment/views.py
from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect

from leases.models import Lease
from users.models import User
from .models import Payment
from .forms import PaymentForm
from django.contrib.auth.decorators import login_required

@login_required
def payment_list(request):
    # Filter payments for the current user (tenant)
    payments = Payment.objects.filter(tenantId=request.user)  # Filtering payments by the logged-in user
    return render(request, 'rent_payment/payment_list.html', {'payments': payments})

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
    unpaid = Lease.objects.filter(tenant=request.user, payment_status='unpaid')  # Check payment_status instead of status
    paid = Lease.objects.filter(tenant=request.user, payment_status='paid')  # Check payment_status here as well
    return render(request, 'rent_payment/pending_list.html', {'unpaid': unpaid, 'paid': paid})
