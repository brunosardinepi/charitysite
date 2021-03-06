from allauth.account import views
from allauth.account.signals import user_logged_in
from allauth.socialaccount import views as social_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.dispatch import receiver
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.views import View

import stripe

from . import config
from . import forms
from .utils import email
from campaign.models import Campaign
from donation.models import Donation
from page.models import Page


stripe.api_key = config.settings['stripe_api_sk']

def home(request):
    donations = Donation.objects.all().aggregate(Sum('amount')).get('amount__sum')
    pages = Page.objects.filter(deleted=False, stripe_verified=True).count()
    campaigns = Campaign.objects.filter(deleted=False).count()
    return render(request, 'home.html', {
        'donations': donations,
        'pages': pages,
        'campaigns': campaigns,
    })

class LoginView(views.LoginView):
    template_name = 'login.html'

class SignupView(views.SignupView):
    template_name = 'signup.html'

class SocialSignupView(social_views.SignupView):
    template_name = 'social_signup.html'

class EmailVerificationSentView(views.EmailVerificationSentView):
    template_name = 'verification_sent.html'

class ConfirmEmailView(views.ConfirmEmailView):
    template_name = 'email_confirm.html'

class ConnectionsView(social_views.ConnectionsView):
    template_name = 'userprofile/social_connections.html'

@login_required
def invite(request):
    form = forms.GeneralInviteForm()
    if request.method == 'POST':
        form = forms.GeneralInviteForm(request.POST)
        if form.is_valid():
            # check if the person we are inviting is already on PageFund
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
                if user.userprofile:
                    return redirect('notes:error_invite_user_exists')
            except User.DoesNotExist:
                pass

            # create the email
            email(form.cleaned_data['email'], "blank", "blank", "pagefund_invitation", {})

            return HttpResponseRedirect(reverse('home'))
    return render(request, 'invite.html', {'form': form})

def handler404(request):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

@receiver(user_logged_in)
def stripe_customer_check(request, user, **kwargs):
    try:
        customer = stripe.Customer.retrieve(request.user.userprofile.stripe_customer_id)
    except stripe.error.InvalidRequestError:
        metadata = {'user_pk': request.user.pk}
        customer = stripe.Customer.create(
            email=request.user.email,
            metadata=metadata
        )

        request.user.userprofile.stripe_customer_id = customer.id
        request.user.save()
