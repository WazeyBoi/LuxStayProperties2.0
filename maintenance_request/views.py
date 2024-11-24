from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from users.models import User
from .models import MaintenanceRequest
from leases.models import Lease
from .forms import MaintenanceRequestForm

@login_required
def maintenance_request_list(request):
    maintenance_requests = MaintenanceRequest.objects.filter(tenantId=request.user)
    paginator = Paginator(maintenance_requests, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'maintenance_request/maintenance_request_list.html', {'page_obj': page_obj})

@login_required
def maintenance_request_create(request, leaseid, tenantid):
    lease = get_object_or_404(Lease, id=leaseid)
    tenant = get_object_or_404(User, id=tenantid)

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.leaseId = lease
            maintenance_request.tenantId = tenant
            maintenance_request.status = 'pending'  # Set default status
            maintenance_request.save()
            return redirect('maintenance_request:maintenance_request_list')
    else:
        form = MaintenanceRequestForm()

    return render(request, 'maintenance_request/maintenance_request_form.html', {
        'form': form,
        'lease': lease,
        'tenant': tenant
    })
@login_required
def owner_maintenance_requests(request):
    # Adjust the filter according to your actual model relationships
    requests = MaintenanceRequest.objects.filter(leaseId__property__owner=request.user)
    return render(request, 'maintenance_request/maintenance_request_ownerlist.html', {
        'requests': requests,
        'has_requests': requests.exists(),
    })

@login_required
def accept_maintenance_request(request, requestid):
    # Get the maintenance request by ID
    maintenance_request = MaintenanceRequest.objects.get(requestId=requestid)
    
    # Change the status to "in_progress" when accepted
    maintenance_request.status = 'in_progress'
    maintenance_request.save()

    # Redirect back to the maintenance request list page for the tenant (or lease)
    return redirect('maintenance_request:maintenance_request_ownerlist')  # Corrected view for tenant's requests

@login_required
def complete_maintenance_request(request, requestid):
    maintenance_request = MaintenanceRequest.objects.get(requestId=requestid)
    maintenance_request.status = 'completed'
    maintenance_request.save()
    return redirect('maintenance_request:maintenance_request_ownerlist')  # Redirect to a relevant page