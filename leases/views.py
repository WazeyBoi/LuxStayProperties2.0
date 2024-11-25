# leases/views.py

from django.shortcuts import render, get_object_or_404, redirect
from datetime import date
from django.contrib.auth.decorators import login_required
from .models import Lease
from properties.models import Property
from datetime import datetime
from django.core.paginator import Paginator
from datetime import datetime, timedelta

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
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        
        # Convert the string dates to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Check if the duration is at least 30 days
        total_days = (end_date - start_date).days
        if total_days < 30:
            context = {
                'property': property_obj,
                'error_message': 'The booking duration must be at least 1 month (30 days).',
            }
            return render(request, 'leases/book_property.html', context)

        # Calculate the total amount for the booking
        if total_days % 30 == 0:
            # If the days are exactly divisible by 30, calculate based on monthly price
            months = total_days // 30
            total_amount = months * property_obj.price
            print(f"Divisible by 30: {total_days} days = {months} months at ${property_obj.price} per month.")
        else:
            # If not divisible by 30, calculate for complete months and extra days
            months = total_days // 30
            extra_days = total_days % 30
            daily_rate = property_obj.price / 30  # Calculate daily rate from monthly price
            total_amount = (months * property_obj.price) + (extra_days * daily_rate)
            print(f"Not divisible by 30: {total_days} days = {months} months + {extra_days} extra days.")
            print(f"Monthly price: ${property_obj.price}, Daily rate: ${daily_rate:.2f}, Total amount: ${total_amount:.2f}.")

        # Create the lease
        lease = Lease.objects.create(
            tenant=request.user,
            property=property_obj,
            start_date=start_date,
            end_date=end_date,
            total_amount=total_amount,
            remaining_balance=total_amount,  # Set the remaining balance to the total amount
            status='pending',
            payment_status='unpaid'
        )
        
        # Update the property status to 'leased'
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