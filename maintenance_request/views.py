# maintenance_request/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from users.models import User
from .models import MaintenanceRequest
from leases.models import Lease
from .forms import MaintenanceRequestForm

@login_required
def maintenance_request_list(request):
    requests = MaintenanceRequest.objects.filter(tenantId=request.user)
    paginator = Paginator(requests, 5)  # 5 items per page
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
    lease = get_object_or_404(Lease, id=leaseid, tenant_id=tenantid)
    tenant = get_object_or_404(User, id=tenantid)

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.leaseId = lease
            request_obj.tenantId = tenant
            request_obj.save()
            return redirect('maintenance_request_list')
    else:
        form = MaintenanceRequestForm()

    return render(request, 'maintenance_request/maintenance_request_form.html', {
        'form': form,
        'lease': lease,
        'tenant': tenant
    })