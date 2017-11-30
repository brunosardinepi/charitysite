import ast

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Sum
from django.http import Http404
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm, get_perms

from . import forms
from . import models
from .utils import campaign_average_duration, campaign_success_pct, campaign_types
from . import views
from campaign import models as CampaignModels
from donation.models import Donation
from invitations.models import ManagerInvitation
from plans.models import StripePlan


class PageTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
        )

        self.user2 = User.objects.create_user(
            username='harrypotter',
            email='harry@potter.com',
            password='imawizard',
        )

        self.user3 = User.objects.create_user(
            username='bobdole',
            email='bob@dole.com',
            password='dogsarecool',
        )

        self.user4 = User.objects.create_user(
            username='batman',
            email='batman@bat.cave',
            password='imbatman',
        )

        self.user5 = User.objects.create_user(
            username='newguy',
            email='its@me.com',
            password='imnewhere',
        )

        self.page = models.Page.objects.create(
            name='Test Page',
            type='Nonprofit',
            nonprofit_number='123456789',
            page_slug='testpage',
            city='Houston',
            state='Texas',
            description='This is a description for Test Page.',
            category='Animal',
            contact_email='contact@page.com',
            contact_phone='111-111-1111',
            website='testpage.com',
        )

        self.page.admins.add(self.user.userprofile)
        self.page.subscribers.add(self.user.userprofile)
        self.page.managers.add(self.user3.userprofile)
        self.page.managers.add(self.user4.userprofile)
        assign_perm('manager_edit', self.user3, self.page)
        assign_perm('manager_delete', self.user3, self.page)
        assign_perm('manager_invite', self.user3, self.page)
        assign_perm('manager_image_edit', self.user3, self.page)
        assign_perm('manager_view_dashboard', self.user3, self.page)

        self.page2 = models.Page.objects.create(
            name='Office',
            type='Personal',
            page_slug='officedesk',
            city='Chicago',
            state='IL',
            description='Im in the office.',
            category='Animal',
            deleted=True,
        )

        self.campaign = CampaignModels.Campaign.objects.create(
            name='Test Campaign',
            page=self.page,
            type='event',
            description='This is a description for Test Campaign.',
            goal='11',
        )

        self.campaign2 = CampaignModels.Campaign.objects.create(
            name='Another One',
            page=self.page,
            type='event',
            description='My cat died yesterday',
            goal='12',
        )

        self.invitation = ManagerInvitation.objects.create(
            invite_to=self.user2.email,
            invite_from=self.user,
            page=self.page,
        )

        self.donation = Donation.objects.create(
            amount=2000,
            comment='I donated!',
            page=self.page,
            user=self.user,
        )

        self.donation2 = Donation.objects.create(
            amount=800,
            comment='I like campaigns.',
            page=self.page,
            campaign=self.campaign,
            user=self.user,
        )

        self.donation3 = Donation.objects.create(
            amount=580,
            comment='Campaign love',
            page=self.page,
            campaign=self.campaign2,
            user=self.user,
        )

        self.plan = StripePlan.objects.create(
            amount=2000,
            page=self.page,
            campaign=self.campaign,
            user=self.user,
            stripe_plan_id="plan_adagD87asg2342huif3whluq3qr",
            stripe_subscription_id="sub_Sh2982SKDnjSADioqdn3s",
            interval="month",
        )

        self.plan2 = StripePlan.objects.create(
            amount=6500,
            page=self.page,
            user=self.user2,
            stripe_plan_id="plan_AS8o7tasdASDh23eads254",
            stripe_subscription_id="sub_87sadfZDSHF8o723rhnu23",
            interval="month",
        )

    def test_page_exists(self):
        pages = models.Page.objects.all()
        self.assertIn(self.page, pages)

    def test_page_creation_time(self):
        page = models.Page.objects.create(name='time tester')
        now = timezone.now()
        self.assertLess(page.created_on, now)

    def test_duplicate_page_slug(self):
        self.client.login(username='testuser', password='testpassword')

        data = {
            'name': "Tester2",
            'page_slug': "testpage"
        }

        response = self.client.post('/create/', data)
        self.assertEqual(models.Page.objects.filter(deleted=False).count(), 1)

    def test_page_status_logged_out(self):
        request = self.factory.get('home')
        request.user = AnonymousUser()
        response = views.page(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.user.first_name, status_code=200)
        self.assertContains(response, self.user.last_name, status_code=200)
        self.assertContains(response, self.page.city, status_code=200)
        self.assertContains(response, self.page.state, status_code=200)
        self.assertContains(response, self.page.type, status_code=200)
        self.assertContains(response, self.page.description, status_code=200)
        self.assertContains(response, self.page.donation_count(), status_code=200)
        self.assertContains(response, int(self.page.donation_money() / 100), status_code=200)
        self.assertContains(response, self.page.category, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, int(self.campaign.donation_money() / 100), status_code=200)
        self.assertContains(response, self.campaign2.name, status_code=200)
        self.assertContains(response, self.campaign2.goal, status_code=200)
        self.assertContains(response, int(self.campaign2.donation_money() / 100), status_code=200)
        self.assertContains(response, self.page.contact_email, status_code=200)
        self.assertContains(response, self.page.contact_phone, status_code=200)
        self.assertContains(response, self.page.website, status_code=200)

    def test_page_status_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.user.first_name, status_code=200)
        self.assertContains(response, self.user.last_name, status_code=200)
        self.assertContains(response, self.page.city, status_code=200)
        self.assertContains(response, self.page.state, status_code=200)
        self.assertContains(response, self.page.type, status_code=200)
        self.assertContains(response, self.page.description, status_code=200)
        self.assertContains(response, self.page.donation_count(), status_code=200)
        self.assertContains(response, int(self.page.donation_money() / 100), status_code=200)
        self.assertContains(response, self.page.category, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign.goal, status_code=200)
        self.assertContains(response, int(self.campaign.donation_money() / 100), status_code=200)
        self.assertContains(response, self.campaign2.name, status_code=200)
        self.assertContains(response, self.campaign2.goal, status_code=200)
        self.assertContains(response, int(self.campaign2.donation_money() / 100), status_code=200)
        self.assertContains(response, self.page.contact_email, status_code=200)
        self.assertContains(response, self.page.contact_phone, status_code=200)
        self.assertContains(response, self.page.website, status_code=200)

    def test_page_admin_logged_out(self):
        response = self.client.get('/%s/' % self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Dashboard", status_code=200)

    def test_page_admin_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/%s/' % self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard", status_code=200)

        response = self.client.get('/%s/dashboard/' % self.page.page_slug)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Page", status_code=200)
        self.assertContains(response, "Delete Page", status_code=200)
        self.assertContains(response, "Invite others to manage Page", status_code=200)
        self.assertContains(response, "Upload and Edit images", status_code=200)
        self.assertContains(response, "/%s/managers/%s/remove/" % (self.page.page_slug, self.user3.pk), status_code=200)
        self.assertContains(response, "/%s/managers/%s/remove/" % (self.page.page_slug, self.user4.pk), status_code=200)

    def test_page_manager_logged_in(self):
        self.client.login(username='bobdole', password='dogsarecool')
        response = self.client.get('/%s/' % self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard", status_code=200)

        response = self.client.get('/%s/dashboard/' % self.page.page_slug)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Page", status_code=200)
        self.assertContains(response, "Delete Page", status_code=200)
        self.assertContains(response, "Invite others to manage Page", status_code=200)
        self.assertContains(response, "Upload and Edit images", status_code=200)
        self.assertNotContains(response, "/%s/managers/%s/remove/" % (self.page.page_slug, self.user3.pk), status_code=200)
        self.assertNotContains(response, "/%s/managers/%s/remove/" % (self.page.page_slug, self.user4.pk), status_code=200)

    def test_page_edit_logged_out(self):
        response = self.client.get('/%s/edit/' % self.page.page_slug)
        self.assertRedirects(response, '/accounts/login/?next=/%s/edit/' % self.page.page_slug, 302, 200)

    def test_page_edit_not_admin(self):
        self.client.login(username='harrypotter', password='imawizard')
        response = self.client.get('/%s/edit/' % self.page.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_page_edit_admin(self):
        data = {
            'name': self.page.name,
            'page_slug': self.page.page_slug,
            'type': 'nonprofit',
            'nonprofit_number': '123456789',
            'category': 'animal',
            'state': 'DE',
            'description': 'New description here!',
            'ssn': '0000',
            'tos_acceptance': True,
            'ein': '000000001',
            'address_line1': '123 Main St.',
            'city': 'Houston',
            'state': 'TX',
            'zipcode': '77008'
        }
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/%s/edit/' % self.page.page_slug, data)
        self.assertRedirects(response, '/%s/' % self.page.page_slug, 302, 200)
        response = self.client.get('/%s/' % self.page.page_slug)
        self.assertContains(response, 'CT', status_code=200)

    def test_page_edit_manager_perms(self):
        request = self.factory.get('home')
        request.user = self.user3
        response = views.page_edit(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)

    def test_page_edit_manager_no_perms(self):
        self.client.login(username='batman', password='imbatman')
        response = self.client.get('/%s/edit/' % self.page.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_page_not_subscribed(self):
        request = self.factory.get('home')
        request.user = self.user2
        response = views.page(request, self.page.page_slug)

        self.assertContains(response, 'name="subscribe"', status_code=200)

    def test_page_subscribed(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page(request, self.page.page_slug)

        self.assertContains(response, 'name="unsubscribe"', status_code=200)

    def test_page_subscribe_redirect(self):
        response = self.client.get('/page/subscribe/%s/subscribe/' % self.page.pk)
        self.assertRedirects(response, '/accounts/login/?next=/page/subscribe/%s/subscribe/' % self.page.pk, 302, 200)

    def test_page_create_logged_out(self):
        response = self.client.get('/create/')
        self.assertRedirects(response, '/accounts/signup/?next=/create/', 302, 200)

    def test_page_create_logged_in(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page_create(request)

        self.assertEqual(response.status_code, 200)

    def test_pageform(self):
        form = forms.PageForm({
            'name': 'Ribeye Steak',
            'type': 'personal',
            'page_slug': 'ribeyesteak',
            'city': 'Atlanta',
            'state': 'GA',
            'category': 'animal',
            'description': 'I like flank steak.',
            'ssn': '0000',
            'tos_acceptance': True,
            'ein': '000000001',
            'address_line1': '123 Main St.',
            'zipcode': '12345'
        })
        self.assertTrue(form.is_valid())
        page = form.save()
        self.assertEqual(page.name, "Ribeye Steak")
        self.assertEqual(page.type, "personal")
        self.assertEqual(page.page_slug, "ribeyesteak")
        self.assertEqual(page.city, "Atlanta")
        self.assertEqual(page.state, "GA")
        self.assertEqual(page.category, "animal")
        self.assertEqual(page.description, "I like flank steak.")

    def test_pageform_blank(self):
        form = forms.PageForm({})
        self.assertFalse(form.is_valid())

    def test_deletepageform(self):
        form = forms.DeletePageForm({
            'name': self.page
        })
        self.assertTrue(form.is_valid())

    def test_delete_page_logged_out(self):
        response = self.client.get('/%s/delete/' % self.page.page_slug)
        self.assertRedirects(response, '/accounts/login/?next=/%s/delete/' % self.page.page_slug, 302, 200)

    def test_delete_page_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/%s/delete/' % self.page.page_slug)

        self.assertRedirects(response, '/', 302, 200)

    def test_delete_page_not_admin(self):
        self.client.login(username='harrypotter', password='imawizard')
        response = self.client.get('/%s/delete/' % self.page.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_delete_page_manager_perms(self):
        self.client.login(username='bobdole', password='dogsarecool')
        response = self.client.get('/%s/delete/' % self.page.page_slug)

        self.assertRedirects(response, '/', 302, 200)

    def test_delete_page_manager_no_perms(self):
        self.client.login(username='batman', password='imbatman')
        response = self.client.get('/%s/edit/' % self.page.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_page_invite_not_admin_not_manager(self):
        self.client.login(username='harrypotter', password='imawizard')
        response = self.client.get('/%s/managers/invite/' % self.page.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_page_invite_admin_not_manager(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.page_invite(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, "Invite", status_code=200)

    def test_page_invite_not_admin_manager_no_perms(self):
        self.client.login(username='batman', password='imbatman')
        response = self.client.get('/%s/managers/invite/' % self.page.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_page_invite_not_admin_manager_perms(self):
        request = self.factory.get('home')
        request.user = self.user3
        response = views.page_invite(request, self.page.page_slug)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, "Invite", status_code=200)

    def test_page_invite(self):
        data = {
            'email': self.user3.email,
            'manager_edit': "True",
            'manager_delete': "True",
            'manager_invite': "True",
            'manager_image_edit': "True",
            'manager_view_dashboard': "True"
        }

        self.client.login(username='testuser', password='testpassword')

        # user is already a manager
        response = self.client.post('/%s/managers/invite/' % self.page.page_slug, data)
        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)

        # user already has an invite
        data['email'] = self.user2.email
        response = self.client.post('/%s/managers/invite/' % self.page.page_slug, data)
        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)

        # user isn't a manager and doesn't have an invite
        data['email'] = self.user5.email
        response = self.client.post('/%s/managers/invite/' % self.page.page_slug, data)
        self.assertTrue(ManagerInvitation.objects.all().count(), 2)
        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)
        # accept the invite and make sure the page has the right perms
        self.client.login(username='newguy', password='imnewhere')
        invitation = ManagerInvitation.objects.get(invite_to=self.user5.email)
        response = self.client.get('/invite/manager/accept/%s/%s/' % (invitation.pk, invitation.key))
        self.assertRedirects(response, invitation.page.get_absolute_url(), 302, 200)
        response = self.client.get('/%s/dashboard/' % invitation.page.page_slug)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Page", status_code=200)
        self.assertContains(response, "Delete Page", status_code=200)
        self.assertContains(response, "Invite others to manage Page", status_code=200)
        self.assertContains(response, "Upload and Edit images", status_code=200)

    def test_page_dashboard_invite(self):
        data = {
            'email': self.user5.email,
            'manager_edit': "True",
            'manager_delete': "True",
            'manager_invite': "True",
            'manager_image_edit': "True",
            'manager_view_dashboard': "False",
        }

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/{}/managers/invite/'.format(self.page.page_slug), data)
        self.assertTrue(ManagerInvitation.objects.all().count(), 2)
        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)

        self.client.login(username='newguy', password='imnewhere')
        invitation = ManagerInvitation.objects.get(invite_to=self.user5.email)
        response = self.client.get('/invite/manager/accept/{}/{}/'.format(invitation.pk, invitation.key))
        self.assertRedirects(response, invitation.page.get_absolute_url(), 302, 200)
        response = self.client.get('/{}/dashboard/'.format(invitation.page.page_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Page")
        self.assertContains(response, "Delete Page")
        self.assertContains(response, "Invite others to manage Page")
        self.assertContains(response, "Upload and Edit images")
        self.assertNotContains(response, "Donation History")

        self.client.login(username='testuser', password='testpassword')
        permissions = []
        permissions.append(str(self.user5.pk) + "_manager_edit")
        permissions.append(str(self.user5.pk) + "_manager_delete")
        permissions.append(str(self.user5.pk) + "_manager_invite")
        permissions.append(str(self.user5.pk) + "_manager_image_edit")
        permissions.append(str(self.user5.pk) + "_manager_view_dashboard")
        data = {'permissions[]': permissions}
        response = self.client.post('/{}/dashboard/'.format(self.page.page_slug), data)

        self.client.login(username='newguy', password='imnewhere')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Page")
        self.assertContains(response, "Delete Page")
        self.assertContains(response, "Invite others to manage Page")
        self.assertContains(response, "Upload and Edit images")
        self.assertContains(response, "Donation History")

    def test_ManagerInviteForm(self):
        data = {
            'email': self.user2.email,
            'manager_edit': "True",
            'manager_delete': "True",
            'manager_invite': "True"
        }
        form = forms.ManagerInviteForm(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form['email'], self.user2.email)
        self.assertTrue(form['manager_edit'], "True")
        self.assertTrue(form['manager_delete'], "True")
        self.assertTrue(form['manager_invite'], "True")

    def test_ManagerInviteForm_blank(self):
        form = forms.ManagerInviteForm({})
        self.assertFalse(form.is_valid())

    def test_remove_manager_logged_out(self):
        response = self.client.get('/%s/managers/%s/remove/' % (self.page.page_slug, self.user3.pk))
        self.assertRedirects(response, '/accounts/login/?next=/%s/managers/%s/remove/' % (self.page.page_slug, self.user3.pk), 302, 200)

    def test_remove_manager_logged_in_not_admin(self):
        self.client.login(username='harrypotter', password='imawizard')
        response = self.client.get('/%s/managers/%s/remove/' % (self.page.page_slug, self.user3.pk))
        self.assertEqual(response.status_code, 404)

    def test_remove_manager_logged_in_admin(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.remove_manager(request, self.page.page_slug, self.user3.pk)
        response.client = self.client

        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)

    def test_remove_manager(self):
        request = self.factory.get('home')
        request.user = self.user
        response = views.remove_manager(request, self.page.page_slug, self.user3.pk)
        response.client = self.client

        managers = self.page.managers.all()
        self.assertNotIn(self.user3, managers)
        self.assertFalse(self.user3.has_perm('manager_edit', self.page))
        self.assertFalse(self.user3.has_perm('manager_delete', self.page))
        self.assertFalse(self.user3.has_perm('manager_invite', self.page))
        self.assertFalse(self.user3.has_perm('manager_image_edit', self.page))
        self.assertRedirects(response, self.page.get_absolute_url(), 302, 200)

    def test_page_permissions_add(self):
        permissions = []
        permissions.append(str(self.user4.pk) + "_manager_edit")
        permissions.append(str(self.user4.pk) + "_manager_delete")
        permissions.append(str(self.user4.pk) + "_manager_invite")
        permissions.append(str(self.user4.pk) + "_manager_image_edit")
        data = {'permissions[]': permissions}

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/%s/' % self.page.page_slug, data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user4.has_perm('manager_edit', self.page))
        self.assertTrue(self.user4.has_perm('manager_delete', self.page))
        self.assertTrue(self.user4.has_perm('manager_invite', self.page))
        self.assertTrue(self.user4.has_perm('manager_image_edit', self.page))

    def test_page_permissions_remove(self):
        permissions = []
        permissions.append(str(self.user3.pk) + "_manager_invite")
        data = {'permissions[]': permissions}

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/%s/' % self.page.page_slug, data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user3.has_perm('manager_edit', self.page))
        self.assertFalse(self.user3.has_perm('manager_delete', self.page))
        self.assertTrue(self.user3.has_perm('manager_invite', self.page))
        self.assertFalse(self.user3.has_perm('manager_image_edit', self.page))

    def test_page_permissions_multiple(self):
        permissions = []
        permissions.append(str(self.user3.pk) + "_manager_invite")
        permissions.append(str(self.user3.pk) + "_manager_image_edit")
        permissions.append(str(self.user4.pk) + "_manager_edit")
        permissions.append(str(self.user4.pk) + "_manager_delete")
        permissions.append(str(self.user4.pk) + "_manager_invite")
        data = {'permissions[]': permissions}

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/%s/' % self.page.page_slug, data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user3.has_perm('manager_edit', self.page))
        self.assertFalse(self.user3.has_perm('manager_delete', self.page))
        self.assertTrue(self.user3.has_perm('manager_invite', self.page))
        self.assertTrue(self.user3.has_perm('manager_image_edit', self.page))
        self.assertTrue(self.user4.has_perm('manager_edit', self.page))
        self.assertTrue(self.user4.has_perm('manager_delete', self.page))
        self.assertTrue(self.user4.has_perm('manager_invite', self.page))
        self.assertFalse(self.user4.has_perm('manager_image_edit', self.page))

    def test_delete_page_view(self):
        response = self.client.get('/%s/' % self.page2.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_upload_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/%s/images/' % self.page.page_slug)
        self.assertEqual(response.status_code, 200)

    def test_upload_manager_perms(self):
        self.client.login(username='bobdole', password='dogsarecool')
        response = self.client.get('/%s/images/' % self.page.page_slug)
        self.assertEqual(response.status_code, 200)

    def test_upload_manager_no_perms(self):
        self.client.login(username='batman', password='imbatman')
        response = self.client.get('/%s/images/' % self.page.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_upload_logged_in_no_perms(self):
        self.client.login(username='newguy', password='imnewhere')
        response = self.client.get('/%s/images/' % self.page.page_slug)
        self.assertEqual(response.status_code, 404)

    def test_upload_logged_out(self):
        response = self.client.get('/%s/images/' % self.page.page_slug)
        self.assertRedirects(response, '/accounts/login/?next=/testpage/images/', 302, 200)

    def test_dashboard_total_donations(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        total_donations = Donation.objects.filter(page=self.page).aggregate(Sum('amount')).get('amount__sum')
        total_donations_count = Donation.objects.filter(page=self.page).count()
        total_donations_avg = int((total_donations / total_donations_count) / 100)
        self.assertContains(response, "Total donated: ${} (Avg: ${})".format(
            int(total_donations / 100),
            total_donations_avg),
            status_code=200)

    def test_dashboard_page_donations(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        page_donations = Donation.objects.filter(page=self.page, campaign__isnull=True).aggregate(Sum('amount')).get('amount__sum')
        page_donations_count = Donation.objects.filter(page=self.page, campaign__isnull=True).count()
        page_donations_avg = int((page_donations / page_donations_count) / 100)
        self.assertContains(response, "Donated to page: ${} (Avg: ${})".format(
            int(page_donations / 100),
            page_donations_avg),
            status_code=200)

    def test_dashboard_campaign_donations(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        campaign_donations = Donation.objects.filter(page=self.page, campaign__isnull=False).aggregate(Sum('amount')).get('amount__sum')
        campaign_donations_count = Donation.objects.filter(page=self.page, campaign__isnull=False).count()
        campaign_donations_avg = int((campaign_donations / campaign_donations_count) / 100)
        self.assertContains(response, "Donated to campaigns: ${} (Avg: ${})".format(
            int(campaign_donations / 100),
            campaign_donations_avg),
            status_code=200)

    def test_dashboard_plan_donations(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        plan_donations = StripePlan.objects.filter(page=self.page, campaign__isnull=True).aggregate(Sum('amount')).get('amount__sum')
        plan_donations_count = StripePlan.objects.filter(page=self.page, campaign__isnull=True).count()
        plan_donations_avg = int((plan_donations / plan_donations_count) / 100)
        self.assertContains(response, "Page recurring donations: ${} (Avg: ${})".format(
            int(plan_donations / 100),
            plan_donations_avg),
            status_code=200)

    def test_dashboard_donation_history(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        self.assertContains(response, self.page.name, status_code=200)
        self.assertContains(response, self.campaign.name, status_code=200)
        self.assertContains(response, self.campaign2.name, status_code=200)

    def test_dashboard_top_donors(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        total_donation_amount = int((self.donation.amount + self.donation2.amount + self.donation3.amount) / 100)
        self.assertContains(response, "${} - {} {}".format(total_donation_amount, self.user.first_name, self.user.last_name), status_code=200)

    def test_dashboard_campaign_types(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        campaigns = campaign_types(self.page)
        for k,v in campaigns.items():
            self.assertContains(response, "Type: {}; Count: {}; Donations: ${}".format(v["display"], v["count"], int(v["sum"] / 100)), status_code=200)

    def test_dashboard_average_campaign_duration(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        self.assertContains(response, "{} days".format(campaign_average_duration(self.page)), status_code=200)

    def test_dashboard_campaign_success_pct(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/{}/dashboard/'.format(self.page.page_slug))

        campaigns = campaign_success_pct(self.page)
        for k,v in campaigns.items():
            self.assertContains(response, "Type: {}; Success Pct: {}".format(v["display"], v["success_pct"]), status_code=200)

    def test_image_upload(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a" * 1024
        image = SimpleUploadedFile("image.png", content, content_type="image/png")
        response = self.client.post('/{}/images/'.format(self.page.page_slug), {'image': image})
        self.assertEqual(response.status_code, 200)

        images = models.PageImage.objects.filter(page=self.page)
        self.assertEqual(len(images), 1)

        image = images[0]
        response = self.client.get('/{}/'.format(self.page.page_slug))
        self.assertContains(response, image.image.url, status_code=200)

        image.delete()
        images = models.PageImage.objects.filter(page=self.page)
        self.assertEqual(len(images), 0)

    def test_image_upload_error_size(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a" * 1024 * 1024 * 5
        image = SimpleUploadedFile("image.png", content, content_type="image/png")
        response = self.client.post('/{}/images/'.format(self.page.page_slug), {'image': image})
        content = response.content.decode('ascii')
        content = ast.literal_eval(content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["is_valid"], "f")
        self.assertEqual(content["redirect"], "error_size")

        images = models.PageImage.objects.filter(page=self.page)
        self.assertEqual(len(images), 0)

    def test_image_upload_error_type(self):
        self.client.login(username='testuser', password='testpassword')
        content = b"a"
        image = SimpleUploadedFile("notimage.txt", content, content_type="text/html")
        response = self.client.post('/{}/images/'.format(self.page.page_slug), {'image': image})
        content = response.content.decode('ascii')
        content = ast.literal_eval(content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["is_valid"], "f")
        self.assertEqual(content["redirect"], "error_type")

        images = models.PageImage.objects.filter(page=self.page)
        self.assertEqual(len(images), 0)

