from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

logger = logging.getLogger(__name__)

from properties.models import Property
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
        'maintenance_requests': page_obj.object_list,
    })

@login_required
def maintenance_request_create(request, propertyid, tenantid):
    property_obj = get_object_or_404(Property, id=propertyid)
    tenant = get_object_or_404(User, id=tenantid)

    if request.method == 'POST':
        logger.info(f"Received data: {request.POST}")
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.propertyId = property_obj
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
    return render(request, 'maintenance_request/maintenance_request_form.html', {'form': form, 'property': property_obj, 'tenant': tenant})

@login_required
def owner_maintenance_requests(request):
    requests = MaintenanceRequest.objects.filter(propertyId__owner=request.user)
    paginator = Paginator(requests, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'maintenance_request/maintenance_request_ownerlist.html', {
        'requests': page_obj,
    })

@login_required
def accept_maintenance_request(request, requestid):
    maintenance_request = get_object_or_404(MaintenanceRequest, requestId=requestid)
    maintenance_request.status = 'in_progress'
    maintenance_request.save()
    return redirect('maintenance_request:maintenance_request_ownerlist')
@login_required
def complete_maintenance_request(request, requestid):
    maintenance_request = get_object_or_404(MaintenanceRequest, requestId=requestid)
    maintenance_request.status = 'completed'
    maintenance_request.save()
    return redirect('maintenance_request:maintenance_request_ownerlist')
