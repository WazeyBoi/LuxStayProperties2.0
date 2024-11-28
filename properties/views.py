from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import User
from .models import Property
from .forms import PropertyForm
from django.core.paginator import Paginator
from leases.models import Lease
from datetime import date
from django.contrib import messages
from rent_payment.models import Payment

@login_required
def property_owner_dashboard(request):
    if request.user.role != 'property_owner':
        return redirect('login')  # Restrict access to PropertyOwners only
    return render(request, 'properties/dashboard.html')

@login_required
def property_listing_management(request):
    # Display only properties owned by the logged-in user
    properties = Property.objects.filter(owner=request.user)
    paginator = Paginator(properties, 5)  # Show 5 properties per page
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)  # Get the properties for the current page

    return render(request, 'properties/property_listing_management.html', {'page_obj': page_obj})

@login_required
def add_property(request):
    if request.method == "POST":
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user  # Set the property owner to the logged-in user
            property.save()
            return redirect('property_listing_management')
    else:
        form = PropertyForm()
    return render(request, 'properties/add_property.html', {'form': form})

@login_required
def update_property(request, property_id):
    property = get_object_or_404(Property, id=property_id, owner=request.user)
    if request.method == "POST":
        form = PropertyForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            return redirect('property_listing_management')
    else:
        form = PropertyForm(instance=property)
    return render(request, 'properties/update_property.html', {'form': form})

@login_required
def delete_property(request, property_id):
    property = get_object_or_404(Property, id=property_id, owner=request.user)
    if request.method == "POST":
        property.delete()
        return redirect('property_listing_management')
    return render(request, 'properties/delete_confirmation.html', {'property': property})

@login_required
def property_bookings(request):
    # Get properties owned by the logged-in user
    properties = Property.objects.filter(owner=request.user)
    
    # Filter leases based on the properties owned by the logged-in user
    active_leases = Lease.objects.filter(property__in=properties, status='active')
    past_leases = Lease.objects.filter(property__in=properties, status='ended')
    terminated_leases = Lease.objects.filter(property__in=properties, status='terminated')

    # Paginate active leases
    active_paginator = Paginator(active_leases, 5)  # Show 10 active leases per page
    active_page_number = request.GET.get('page')
    active_page_obj = active_paginator.get_page(active_page_number)

    # Paginate past leases
    past_paginator = Paginator(past_leases, 5)  # Show 10 past leases per page
    past_page_number = request.GET.get('past_page')
    past_page_obj = past_paginator.get_page(past_page_number)

    # Paginate terminated leases
    terminated_paginator = Paginator(terminated_leases, 5)  # Show 10 terminated leases per page
    terminated_page_number = request.GET.get('terminated_page')
    terminated_page_obj = terminated_paginator.get_page(terminated_page_number)

    context = {
        'page_obj': active_page_obj,
        'past_page_obj': past_page_obj,
        'terminated_page_obj': terminated_page_obj,
    }
    return render(request, 'leases/property_bookings.html', context)

@login_required
def terminate_lease(request, lease_id):
    lease = get_object_or_404(Lease, id=lease_id)

    if request.method == 'POST':
        # Update the property's status to available
        lease.property.status = 'available'
        lease.property.save()

        # Mark the lease as inactive
        lease.end_date = date.today()  # Set the end date to today
        lease.status = 'terminated'  # Ensure lease status is inactive
        lease.save()


        return redirect('property_bookings')

    return render(request, 'leases/terminate_confirmation.html', {'lease': lease})
    
@login_required
def terminate_confirmation(request, lease_id):
    lease = get_object_or_404(Lease, id=lease_id)
    return render(request, 'leases/terminate_confirmation.html', {'lease': lease})

@login_required
def property_payment(request):
    if request.user.role != 'property_owner':
        return redirect('login')  # Restrict access to PropertyOwners only

    # Fetch the payment information related to active leases for properties owned by the logged-in user
    payments = Payment.objects.filter(
        leaseId__property__owner=request.user,
        leaseId__status='active'  # Filter by active leases
    ).select_related('tenantId', 'leaseId__property')  # Optimized query to access related models

    context = {
        'payments': payments,
    }

    return render(request, 'properties/property_payment.html', context)

#test