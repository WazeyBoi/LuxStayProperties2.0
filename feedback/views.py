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
    lease = get_object_or_404(Lease, id=leaseid, tenant_id=tenantid)
    tenant = get_object_or_404(User, id=tenantid)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.leaseId = lease
            feedback.tenantId = tenant
            feedback.save()
            return redirect('feedback_list')
    else:
        form = FeedbackForm()

    return render(request, 'feedback/feedback_form.html', {
        'form': form,
        'lease': lease,
        'tenant': tenant
    })
