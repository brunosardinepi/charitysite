from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

import stripe

from . import forms
from . import models
from donation.models import Donation
from invitations.models import ManagerInvitation
from page import models as PageModels


@login_required
def userprofile(request):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    if userprofile.user == request.user:
        userimages = models.UserImages.objects.filter(user=request.user.id)
        userprofileimage = models.UserImages.objects.filter(user=request.user.id, profile_picture=True)
        admin_pages = userprofile.page_admins.filter(deleted=False)
        manager_pages = userprofile.page_managers.filter(deleted=False)
        subscriptions = userprofile.subscribers.filter(deleted=False)
        campaigns = userprofile.campaign_admins.filter(deleted=False)
        invitations = ManagerInvitation.objects.filter(invite_from=request.user, expired=False)
        donations = Donation.objects.filter(user=request.user)

        sc = stripe.Customer.retrieve(userprofile.stripe_customer_id).sources.all(object='card')
        cards = {}
        for c in sc:
            card = get_object_or_404(models.StripeCard, stripe_card_id=c.id)
            cards[card.id] = {
                'exp_month': c.exp_month,
                'exp_year': c.exp_year,
                'name': card.name,
                'id': card.id
            }

        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'state': request.user.userprofile.state,
            'birthday': request.user.userprofile.birthday
        }
        form = forms.UserProfileForm(data)
        if request.method == 'POST':
            form = forms.UserProfileForm(request.POST)
            if form.is_valid():
                form.save()
            return HttpResponseRedirect(userprofile.get_absolute_url())
        return render(request, 'userprofile/profile.html', {
            'userprofile': userprofile,
            'userimages': userimages,
            'userprofileimage': userprofileimage,
            'admin_pages': admin_pages,
            'manager_pages': manager_pages,
            'subscriptions': subscriptions,
            'campaigns': campaigns,
            'invitations': invitations,
            'form': form,
            'cards': cards,
            'donations': donations
        })
    else:
        raise Http404

@login_required
def profile_image_upload(request):
    userprofile = get_object_or_404(models.UserProfile, user_id=request.user.id)
    form = forms.UserImagesForm(instance=userprofile)
    if request.method == 'POST':
        form = forms.UserImagesForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('image',False)
            image_type = image.content_type.split('/')[0]
            if image_type in settings.UPLOAD_TYPES:
                if image._size > settings.MAX_IMAGE_UPLOAD_SIZE:
                    return redirect('error:error_image_size')
                imageupload = form.save(commit=False)
                imageupload.user_id=request.user.id
                try:
                    profile = models.UserImages.objects.get(user=userprofile, profile_picture=True)
                except models.UserImages.DoesNotExist:
                    profile = None
                if profile and imageupload.profile_picture:
                    profile.profile_picture=False
                    profile.save()
                imageupload.user_id=request.user.id
                imageupload.save()
                return HttpResponseRedirect(userprofile.get_absolute_url())
            else:
                raise ValidationError('This is not an imagee')
    return render(request, 'userprofile/profile_image_upload.html', {'userprofile': userprofile, 'form': form })

@login_required
def update_card(request):
    if request.method == "POST":
#        form = forms.UpdateCardForm(data=request.POST)
#        if form.is_valid():
        card = get_object_or_404(models.StripeCard, pk=request.POST.get('id'))
        if request.user.userprofile == card.user:
            card.name = request.POST.get('name')
            card.save()
            customer = stripe.Customer.retrieve(request.user.userprofile.stripe_customer_id)
            stripe_card = customer.sources.retrieve(card.stripe_card_id)
            stripe_card.exp_month = request.POST.get('exp_month')
            stripe_card.exp_year = request.POST.get('exp_year')
            stripe_card.save()
            return HttpResponseRedirect(card.user.get_absolute_url())
