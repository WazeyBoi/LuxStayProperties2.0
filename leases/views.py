# leases/views.py

from django.shortcuts import render, get_object_or_404, redirect
from datetime import date
from django.contrib.auth.decorators import login_required
from .models import Lease, Property
from datetime import datetime
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.db.models import Q

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
        if total_days == 365:  # Exactly 12 months
            total_amount = property_obj.price * 12
            print(f"Booking for 12 months: ${property_obj.price} per month * 12 months = ${total_amount}.")
        elif total_days % 30 == 0:
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
    # Fetch only available properties
    properties = Property.objects.filter(status='available')
    
    # Fetch dropdown values
    property_types = [choice[0] for choice in Property.PROPERTY_TYPE_CHOICES]
    furnished_status = [True, False]  # For 'is_furnished' dropdown
    pet_policies = [True, False]  # For 'pet_policy' dropdown
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    property_type = request.GET.get('property_type', '')
    is_furnished = request.GET.get('is_furnished', '')
    pet_policy = request.GET.get('pet_policy', '')
    rooms_min = request.GET.get('rooms_min', '')
    rooms_max = request.GET.get('rooms_max', '')
    baths_min = request.GET.get('baths_min', '')
    baths_max = request.GET.get('baths_max', '')
    square_ft_min = request.GET.get('square_ft_min', '')
    square_ft_max = request.GET.get('square_ft_max', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    parking_spaces_min = request.GET.get('parking_spaces_min', '')
    parking_spaces_max = request.GET.get('parking_spaces_max', '')

    # Apply filters
    if search_query:
        properties = properties.filter(
            Q(property_name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    if property_type:
        properties = properties.filter(property_type=property_type)
    if is_furnished in ['True', 'False']:
        properties = properties.filter(is_furnished=(is_furnished == 'True'))
    if pet_policy in ['True', 'False']:
        properties = properties.filter(pet_policy=(pet_policy == 'True'))
    if rooms_min.isdigit():
        properties = properties.filter(number_of_rooms__gte=int(rooms_min))
    if rooms_max.isdigit():
        properties = properties.filter(number_of_rooms__lte=int(rooms_max))
    if baths_min.isdigit():
        properties = properties.filter(num_of_bathrooms__gte=int(baths_min))
    if baths_max.isdigit():
        properties = properties.filter(num_of_bathrooms__lte=int(baths_max))
    if square_ft_min.isdigit():
        properties = properties.filter(sqft__gte=int(square_ft_min))
    if square_ft_max.isdigit():
        properties = properties.filter(sqft__lte=int(square_ft_max))
    if price_min.isdigit():
        properties = properties.filter(price__gte=int(price_min))
    if price_max.isdigit():
        properties = properties.filter(price__lte=int(price_max))
    if parking_spaces_min.isdigit():
        properties = properties.filter(parking_spaces__gte=int(parking_spaces_min))
    if parking_spaces_max.isdigit():
        properties = properties.filter(parking_spaces__lte=int(parking_spaces_max))
    
    context = {
        'properties': properties,
        'property_types': property_types,
        'furnished_status': furnished_status,
        'pet_policies': pet_policies,
        'search_query': search_query,
        'property_type': property_type,
        'is_furnished': is_furnished,
        'pet_policy': pet_policy,
        'rooms_min': rooms_min,
        'rooms_max': rooms_max,
        'baths_min': baths_min,
        'baths_max': baths_max,
        'square_ft_min': square_ft_min,
        'square_ft_max': square_ft_max,
        'price_min': price_min,
        'price_max': price_max,
        'parking_spaces_min': parking_spaces_min,
        'parking_spaces_max': parking_spaces_max,
    }
    
    return render(request, 'properties/property_listing.html', context)

@login_required
def view_property_details(request, property_id):
    # Retrieve the property by ID
    property = get_object_or_404(Property, id=property_id)

    # Pass the property to the template
    return render(request, 'properties/view_property_details.html', {'property': property})

#test