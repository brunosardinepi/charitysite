from django.core import serializers
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime

from . import forms
from . import models
from campaign.models import Campaign
from page.models import Page

import json


def comment_page(request, page_pk):
    page = get_object_or_404(Page, pk=page_pk)
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        response_data = {}

        comment = models.Comment.objects.create(
            user=request.user,
            content=comment_text,
            page=page
        )

        response_data['content'] = comment.content
        response_data['user'] = "%s %s" % (comment.user.userprofile.first_name, comment.user.userprofile.last_name)
        response_data['date'] = localtime(comment.date)
        response_data['date'] = response_data['date'].strftime('%m/%d/%y %-I:%M %p')
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

def reply(request, comment_pk):
    comment = get_object_or_404(models.Comment, pk=comment_pk)
    if request.method == 'POST':
        reply_text = request.POST.get('reply_text')
        response_data = {}

        reply = models.Reply.objects.create(
            user=request.user,
            content=reply_text,
            comment=comment
        )

        response_data['content'] = reply.content
        response_data['user'] = "%s %s" % (reply.user.userprofile.first_name, reply.user.userprofile.last_name)
        response_data['date'] = localtime(reply.date)
        response_data['date'] = response_data['date'].strftime('%m/%d/%y %-I:%M %p')
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

def comment_campaign(request, campaign_pk):
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    form = forms.CommentForm()
    if request.method == 'POST':
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.campaign = campaign
            comment.save()
            return HttpResponseRedirect(campaign.get_absolute_url())
        else:
            return Http404
