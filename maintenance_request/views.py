from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

logger = logging.getLogger(__name__)

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

    return render(request, 'maintenance_request/maintenance_request_list.html', {
        'page_obj': page_obj,
        'maintenance_requests': page_obj.object_list,  # Pass current page objects if needed in the template
    })

@login_required
def maintenance_request_create(request, leaseid, tenantid):
    lease = get_object_or_404(Lease, id=leaseid)
    tenant = get_object_or_404(User, id=tenantid)

    if request.method == 'POST':
        logger.info(f"Received data: {request.POST}")  # Log incoming data
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.leaseId = lease
            maintenance_request.tenantId = tenant
            maintenance_request.status = 'pending'
            maintenance_request.subject = form.cleaned_data['subject']
            maintenance_request.description = form.cleaned_data['description']
            maintenance_request.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('maintenance_request:maintenance_request_list')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = MaintenanceRequestForm()
    return render(request, 'maintenance_request/maintenance_request_form.html', {'form': form, 'lease': lease, 'tenant': tenant})

@login_required
def owner_maintenance_requests(request):
    # Adjust the filter according to your actual model relationships
    requests = MaintenanceRequest.objects.filter(leaseId__property__owner=request.user)
    paginator = Paginator(requests, 5)  # Display 5 requests per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'maintenance_request/maintenance_request_ownerlist.html', {
        'requests': page_obj,  # Paginated object
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