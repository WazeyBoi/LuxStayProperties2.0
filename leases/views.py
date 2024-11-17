# leases/views.py

from django.shortcuts import render, get_object_or_404, redirect
from datetime import date
from django.contrib.auth.decorators import login_required
from .models import Lease
from properties.models import Property
from datetime import datetime
from django.core.paginator import Paginator

@login_required
def tenant_dashboard(request):
    # Filter active leases with unpaid status
    active_leases = Lease.objects.filter(tenant=request.user, status='active', payment_status='unpaid', end_date__gte=date.today())
    inactive_leases = Lease.objects.filter(tenant=request.user, status='inactive')

    context = {
        'active_leases': active_leases,
        'inactive_leases': inactive_leases,
    }
    return render(request, 'leases/tenant_dashboard.html', context)


@login_required
def book_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, status='available')
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Use the property's monthly price as the total amount
        total_amount = property_obj.price

        # Save the lease with status as 'pending'
        lease = Lease(
            tenant=request.user,
            property=property_obj,
            start_date=start_date,
            end_date=end_date,
            total_amount=total_amount,
            status='pending',  # Changed status to 'pending'
            payment_status='unpaid'  # New field added here
        )
        lease.save()
        
        # Update property status to 'leased'
        property_obj.status = 'leased'
        property_obj.save()

        return redirect('tenant_dashboard')
    
    return render(request, 'leases/book_property.html', {'property': property_obj})

@login_required
def my_bookings(request):
    # Filter bookings
    active_bookings = Lease.objects.filter(tenant=request.user, status='active')
    pending_bookings = Lease.objects.filter(tenant=request.user, status='pending')
    old_bookings = Lease.objects.filter(tenant=request.user, status__in=['inactive', 'terminated'])

    # Paginate bookings
    paginator_active = Paginator(active_bookings, 5)  # 5 rows per page for active bookings
    paginator_pending = Paginator(pending_bookings, 5)  # 5 rows per page for pending bookings
    paginator_old = Paginator(old_bookings, 5)  # 5 rows per page for old bookings

    # Get current page numbers
    page_active = request.GET.get('page_active', 1)
    page_pending = request.GET.get('page_pending', 1)
    page_old = request.GET.get('page_old', 1)

    # Get the corresponding page objects
    active_page = paginator_active.get_page(page_active)
    pending_page = paginator_pending.get_page(page_pending)
    old_page = paginator_old.get_page(page_old)

    return render(request, 'leases/my_bookings.html', {
        'active_page': active_page,
        'pending_page': pending_page,
        'old_page': old_page,
    })


@login_required
def property_listing(request):
    available_properties = Property.objects.filter(status='available')
    return render(request, 'properties/property_listing.html', {'properties': available_properties})

@login_required
def view_property_details(request, property_id):
    # Retrieve the property by ID
    property = get_object_or_404(Property, id=property_id)

    # Pass the property to the template
    return render(request, 'properties/view_property_details.html', {'property': property})

#test