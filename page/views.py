from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect

from . import forms
from . import models
from campaign import models as CampaignModels
from userprofile.models import UserProfile

import json


def page(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    active_campaigns = CampaignModels.Campaign.objects.filter(page=page, is_active=True)
    inactive_campaigns = CampaignModels.Campaign.objects.filter(page=page, is_active=False)
    try:
        user_subscription_check = page.subscribers.get(user_id=request.user.pk)
    except UserProfile.DoesNotExist:
        user_subscription_check = None
    if user_subscription_check:
        subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe", "color": "red"}
    else:
        subscribe_attr = {"name": "subscribe", "value": "Subscribe", "color": "green"}
    return render(request, 'page/page.html', {
                                            'page': page,
                                            'active_campaigns': active_campaigns,
                                            'inactive_campaigns': inactive_campaigns,
                                            'subscribe_attr': subscribe_attr
                                            })

@login_required
def page_edit(request, page_slug):
    page = get_object_or_404(models.Page, page_slug=page_slug)
    if request.user.userprofile in page.admins.all():
        form = forms.PageForm(instance=page)
        if request.method == 'POST':
            form = forms.PageForm(instance=page, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(page.get_absolute_url())
    else:
        raise Http404
    return render(request, 'page/page_edit.html', {'page': page, 'form': form})

def subscribe(request, page_pk, action=None):
    page = get_object_or_404(models.Page, pk=page_pk)
    if action == "subscribe":
        page.subscribers.add(request.user.userprofile)
        new_subscribe_attr = {"name": "unsubscribe", "value": "Unsubscribe", "color": "red"}
    elif action == "unsubscribe":
        page.subscribers.remove(request.user.userprofile)
        new_subscribe_attr = {"name": "subscribe", "value": "Subscribe", "color": "green"}
    else:
        print("something went wrong")
    new_subscribe_attr = json.dumps(new_subscribe_attr)
    return HttpResponse(new_subscribe_attr)
