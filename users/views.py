from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import User
from leases.models import Lease
from .forms import CustomUserCreationForm
from datetime import date
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.messages import constants

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Redirect based on user role
                if user.role == 'tenant':
                    return redirect('tenant_dashboard')  # Redirect tenants to the tenant dashboard
                elif user.role == 'property_owner':
                    return redirect('property_listing_management')  # Redirect property owners to their dashboard
                
                # Default redirect (if needed)
                return redirect('home')  # Replace 'home' with a suitable default page if needed
            else:
                messages.error(request, "Username or Password is incorrect", extra_tags='login')
        else:
            messages.error(request, "Username or Password is incorrect", extra_tags='login')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required
def tenant_management(request):
    search_query = request.GET.get("search", "").strip()

    if search_query:
        # Filter tenants by first name or last name, excluding superusers
        tenants = User.objects.filter(
            role='tenant',
            is_superuser=False
        ).filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
        )
    else:
        # Default to showing all tenants, excluding superusers
        tenants = User.objects.filter(
            role='tenant',
            is_superuser=False
        )

    # Add active and inactive leases for each tenant
    for tenant in tenants:
        tenant.active_leases = Lease.objects.filter(tenant=tenant, end_date__gte=date.today())
        tenant.inactive_leases = Lease.objects.filter(tenant=tenant, end_date__lt=date.today())

    # Paginate the tenants
    paginator = Paginator(tenants, 5)  # Show 10 tenants per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'users/tenant_management.html', {'page_obj': page_obj, 'search_query': search_query})

@login_required
def tenant_landing_page(request):
    # Check if the logged-in user has the role 'tenant'
    if request.user.role != 'tenant':
        return redirect('login')  # Redirect to login or another page if the user is not a tenant

    return render(request, 'users/tenant_landing_page.html')

@login_required
def view_tenant_lease(request, tenant_id):
    tenant = get_object_or_404(User, id=tenant_id, role='tenant')

    # Fetch active, inactive, and terminated leases
    active_leases = Lease.objects.filter(tenant=tenant, status='active')
    inactive_leases = Lease.objects.filter(tenant=tenant, status='inactive')
    terminated_leases = Lease.objects.filter(tenant=tenant, status='terminated')

    # Pass data to the template
    context = {
        'tenant': tenant,
        'active_leases': active_leases,
        'inactive_leases': inactive_leases,
        'terminated_leases': terminated_leases,
    }
    return render(request, 'users/view_lease.html', context)

@login_required
def edit_account(request):
    user = request.user  # Fetch the currently logged-in user
    if request.method == 'POST':
        current_password = request.POST.get('current_password')

        # Validate current password
        if not check_password(current_password, user.password):
            messages.error(request, "Incorrect current password.")
            return render(request, 'users/edit_account.html', {'user': user})

        # Update user details
        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.contact = request.POST.get('contact', user.contact)
        user.address = request.POST.get('address', user.address)
        user.province = request.POST.get('province', user.province)
        user.city = request.POST.get('city', user.city)
        user.zipcode = request.POST.get('zipcode', user.zipcode)

        # Update password if provided
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')
        if new_password:
            if new_password == confirm_new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Prevent logout after password change
            else:
                messages.error(request, "New passwords do not match.")
                return render(request, 'users/edit_account.html', {'user': user})

        user.save()
        return redirect('tenant_dashboard')

    return render(request, 'users/edit_account.html', {'user': user})

@login_required
def edit_account_property_owner(request):
    user = request.user  # Fetch the currently logged-in user
    if user.role != 'property_owner':
        messages.error(request, "Access denied. This page is for Property Owners only.")
        return redirect('home')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')

        # Validate current password
        if not check_password(current_password, user.password):
            messages.error(request, "Incorrect current password.")
            return render(request, 'users/edit_account_property_owner.html', {'user': user})

        # Update user details
        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.contact = request.POST.get('contact', user.contact)
        user.address = request.POST.get('address', user.address)
        user.province = request.POST.get('province', user.province)
        user.city = request.POST.get('city', user.city)
        user.zipcode = request.POST.get('zipcode', user.zipcode)

        # Update password if provided
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')
        if new_password:
            if new_password == confirm_new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Prevent logout after password change
            else:
                messages.error(request, "New passwords do not match.")
                return render(request, 'users/edit_account_property_owner.html', {'user': user})

        user.save()
        return redirect('property_owner_dashboard')

    return render(request, 'users/edit_account_property_owner.html', {'user': user})
