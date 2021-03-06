from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from invitations.models import ManagerInvitation
from pagefund import config
from pagefund.utils import email


def invite(data):
    form = data["form"]
    request = data["request"]
    page = data["page"]
    campaign = data["campaign"]

    # check if the person we are inviting is already a manager
    try:
        user = User.objects.get(email=form.cleaned_data["email"])
        if user:
            if page:
                if user.userprofile in page.managers.all():
                    status = True
            elif campaign:
                if user.userprofile in campaign.campaign_managers.all():
                    status = True
    except User.DoesNotExist:
        pass

    # check if the user has already been invited by this admin/manager for this page
    # expired should be False, otherwise the previous invitation has expired and we are OK with them getting a new one
    # accepted/declined are irrelevant if the invite has expired, so we don't check these
    if page:
        try:
            invitation = ManagerInvitation.objects.get(
                invite_to=form.cleaned_data['email'],
                invite_from=request.user,
                page=page,
                expired=False
            )
        except ManagerInvitation.DoesNotExist:
            invitation = None
    elif campaign:
        try:
            invitation = ManagerInvitation.objects.get(
                invite_to=form.cleaned_data['email'],
                invite_from=request.user,
                campaign=campaign,
                expired=False
            )
        except ManagerInvitation.DoesNotExist:
            invitation = None

    # if this user has already been invited, redirect the admin/manager
    # need to notify the admin/manager that the person has already been invited
    if invitation:
        # this user has already been invited, so do nothing
        status = True
    # if the user hasn't been invited already, create the invite and send it to them
    else:
        substitutions = {}
        # create the invitation object and set the permissions
        if page:
            invitation = ManagerInvitation.objects.create(
                invite_to=form.cleaned_data['email'],
                invite_from=request.user,
                page=page,
                manager_edit=form.cleaned_data['manager_edit'],
                manager_delete=form.cleaned_data['manager_delete'],
                manager_invite=form.cleaned_data['manager_invite'],
                manager_image_edit=form.cleaned_data['manager_image_edit'],
                manager_view_dashboard=form.cleaned_data['manager_view_dashboard'],
            )

            # send an email for the invitation
            substitutions = {
                "-pagename-": page.name,
                "-invitationurl-": "{}/invite/manager/accept/{}/{}/".format(config.settings['site'], invitation.pk, invitation.key),
            }
            email(form.cleaned_data['email'], "blank", "blank", "page_manager_invitation", substitutions)

        elif campaign:
            invitation = ManagerInvitation.objects.create(
                invite_to=form.cleaned_data['email'],
                invite_from=request.user,
                campaign=campaign,
                manager_edit=form.cleaned_data['manager_edit'],
                manager_delete=form.cleaned_data['manager_delete'],
                manager_invite=form.cleaned_data['manager_invite'],
                manager_image_edit=form.cleaned_data['manager_image_edit'],
                manager_view_dashboard=form.cleaned_data['manager_view_dashboard'],
            )

            # send an email for the invitation
            substitutions = {
                "-campaignname-": campaign.name,
                "-invitationurl-": "{}/invite/manager/accept/{}/{}/".format(config.settings['site'], invitation.pk, invitation.key),
            }
            email(form.cleaned_data['email'], "blank", "blank", "campaign_manager_invitation", substitutions)

        # redirect the admin/manager to the Page
        status = True
    return status

def remove_invitation(invitation_pk, type, accepted, declined):
    if type == 'manager':
        invitation = get_object_or_404(ManagerInvitation, pk=invitation_pk)
    invitation.expired = True
    invitation.accepted = accepted
    invitation.declined = declined
    invitation.save()

def invitation_is_good(request, invitation, key):
    if (key == invitation.key) and (request.user.email == invitation.invite_to):
        return True
    else:
        return False
