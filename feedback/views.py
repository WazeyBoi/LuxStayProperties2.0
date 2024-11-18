# feedback/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from users.models import User
from .models import Feedback
from leases.models import Lease
from .forms import FeedbackForm

@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.filter(tenantId=request.user)
    paginator = Paginator(feedbacks, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'feedback/feedback_list.html', {'page_obj': page_obj})

@login_required
def feedback_create(request, leaseid, tenantid):
    lease = get_object_or_404(Lease, id=leaseid)
    tenant = get_object_or_404(User, id=tenantid)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.leaseId = lease
            feedback.tenantId = tenant
            feedback.save()
            return redirect('feedback:feedback_list')  # Use the correct URL name
    else:
        form = FeedbackForm()  # Ensure the form is initialized for GET requests

    return render(request, 'feedback/feedback_form.html', {
        'form': form,
        'lease': lease,
        'tenant': tenant,
        'stars': range(1, 11), 
    })



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
