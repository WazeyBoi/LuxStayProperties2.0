from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from users.models import User
from .models import Feedback
from leases.models import Lease
from .forms import FeedbackForm

@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.filter(tenantId=request.user)
    paginator = Paginator(feedbacks, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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
            feedback.status = 'new'
            feedback.save()
            return redirect('feedback:feedback_list')
        else:
            print(form.errors)  # For debugging
    else:
        form = FeedbackForm()

    emojis = ["angry", "sad-face", "neutral-face", "smile", "satisfied"]
    stars_with_emojis = [(i, emojis[i - 1]) for i in range(1, 6)]

    context = {
        'form': form,
        'lease': lease,
        'tenant': tenant,
        'stars_with_emojis': stars_with_emojis,
    }

    return render(request, 'feedback/feedback_form.html', context)


@login_required
def feedback_ownerlist(request):
    feedbacks = Feedback.objects.filter(leaseId__property__owner=request.user)
    return render(request, 'feedback/feedback_ownerlist.html', {'feedbacks': feedbacks})

@login_required
def mark_feedback_as_viewed(request, feedbackId):
    feedback = get_object_or_404(Feedback, feedbackId=feedbackId)  # Use feedbackId

    if feedback.leaseId.property.owner != request.user:
        return redirect('feedback:feedback_ownerlist')

    feedback.status = 'viewed'
    feedback.save()
    return redirect('feedback:feedback_ownerlist')
