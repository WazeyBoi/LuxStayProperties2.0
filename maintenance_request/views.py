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

