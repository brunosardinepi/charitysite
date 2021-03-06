from unittest import mock
import datetime
import django
import os
import pytz

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core import mail
from django.db.models import Sum
from django.test import Client, RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.timezone import now

from allauth.account.auth_backends import AuthenticationBackend
from allauth.account.forms import BaseSignupForm
from allauth.account.signals import user_signed_up
from allauth.account import app_settings
from allauth.utils import get_user_model, get_username_max_length
import sendgrid
from sendgrid.helpers.mail import *

from . import views
from campaign.models import Campaign
from donation.models import Donation
from page.models import Page
from pagefund import config


class EmailTest(TestCase):
    def test_email(self):
        sg = sendgrid.SendGridAPIClient(apikey=config.settings["sendgrid_api_key"])
        from_email = Email("no-reply@page.fund")
        to_email = Email("gn9012@gmail.com")
        subject = "Test email"
        content = Content("text/plain", "Test email sent at {}".format(datetime.datetime.now()))
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())

        self.assertEqual(response.status_code, 202)


class SignupTest(TestCase):
    def test_user_signed_up_signal(self):
        self.signal_was_called = False

        def handler(sender, **kwargs):
            self.signal_was_called = True

        user_signed_up.connect(handler)

        data = {
#            'first_name': 'Testing',
#            'last_name': 'Signup',
#            'birthday': '11/12/90',
#            'state': 'CO',
            'email': 'mytestemail@gmail.com',
            'email2': 'mytestemail@gmail.com',
            'password1': 'mytestpassword2',
            'password2': 'mytestpassword2',
        }
        response = self.client.post('/accounts/signup/', data)

        self.assertTrue(self.signal_was_called)

        user_signed_up.disconnect(handler)


class HomeTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.test',
            password='testpassword',
            first_name = 'John',
            last_name = 'Doe'
        )

        self.user2 = User.objects.create_user(
            username='anotherguy',
            email='another@guy.me',
            password='imthatguy',
        )

        self.page = Page.objects.create(name="Buffalo", page_slug="buffalo", is_sponsored=True, trending_score=30.0)
        self.page2 = Page.objects.create(name="Antelope", page_slug="antelope", is_sponsored=False, trending_score=29.0)
        self.page3 = Page.objects.create(name="page3", page_slug="page3", is_sponsored=False, trending_score=28.0)
        self.page4 = Page.objects.create(name="page4", page_slug="page4", is_sponsored=False, trending_score=27.0)
        self.page5 = Page.objects.create(name="page5", page_slug="page5", is_sponsored=False, trending_score=26.0)
        self.page6 = Page.objects.create(name="page6", page_slug="page6", is_sponsored=False, trending_score=25.0)
        self.page7 = Page.objects.create(name="page7", page_slug="page7", is_sponsored=False, trending_score=24.0)
        self.page8 = Page.objects.create(name="page8", page_slug="page8", is_sponsored=False, trending_score=23.0)
        self.page9 = Page.objects.create(name="page9", page_slug="page9", is_sponsored=False, trending_score=22.0)
        self.page10 = Page.objects.create(name="page10", page_slug="page10", is_sponsored=False, trending_score=21.0)
        self.page11 = Page.objects.create(name="page11", page_slug="page11", is_sponsored=False, trending_score=5.0)

        self.page.subscribers.add(self.user.userprofile)

        self.campaign = Campaign.objects.create(
            name="Blue",
            campaign_slug="blue",
            page=self.page,
            trending_score=30.0,
            goal='1',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign2 = Campaign.objects.create(
            name="Green",
            campaign_slug="green",
            page=self.page,
            trending_score=29.0,
            goal='2',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign3 = Campaign.objects.create(
            name="Yellow",
            campaign_slug="yellow",
            page=self.page,
            trending_score=28.0,
            goal='3',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign4 = Campaign.objects.create(
            name="campaign4",
            campaign_slug="campaign4",
            page=self.page2,
            trending_score=27.0,
            goal='4',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign5 = Campaign.objects.create(
            name="campaign5",
            campaign_slug="campaign5",
            page=self.page2,
            trending_score=26.0,
            goal='5',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign6 = Campaign.objects.create(
            name="campaign6",
            campaign_slug="campaign6",
            page=self.page2,
            trending_score=25.0,
            is_active=False,
            goal='6',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign7 = Campaign.objects.create(
            name="campaign7",
            campaign_slug="campaign7",
            page=self.page2,
            trending_score=24.0,
            goal='7',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign8 = Campaign.objects.create(
            name="campaign8",
            campaign_slug="campaign8",
            page=self.page2,
            trending_score=23.0,
            goal='8',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign9 = Campaign.objects.create(
            name="campaign9",
            campaign_slug="campaign9",
            page=self.page2,
            trending_score=22.0,
            goal='9',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign10 = Campaign.objects.create(
            name="campaign10",
            campaign_slug="campaign10",
            page=self.page2,
            trending_score=21.0,
            goal='10',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign11 = Campaign.objects.create(
            name="campaign11",
            campaign_slug="campaign11",
            page=self.page2,
            trending_score=20.0,
            goal='11',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )
        self.campaign12 = Campaign.objects.create(
            name="campaign12",
            campaign_slug="campaign12",
            page=self.page2,
            trending_score=2.0,
            goal='12',
            end_date=datetime.datetime(2099, 8, 15, 8, 15, 12, 0, pytz.UTC),
        )

        self.donation = Donation.objects.create(
            amount=2000,
            comment='I donated!',
            page=self.page,
            user=self.user
        )

        self.donation2 = Donation.objects.create(
            amount=3500,
            comment='Get good.',
            page=self.page,
            user=self.user
        )

        self.donation3 = Donation.objects.create(
            amount=6000,
            comment='I am rich.',
            page=self.page,
            user=self.user2
        )

    def test_admin(self):
        response = self.client.get('/admin/')
        self.assertRedirects(response, '/notes/error/page/does-not-exist/', 302, 200)

    def test_home_logged_out(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/invite/', status_code=200)
        self.assertContains(response, "Get started")

    def test_home_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/invite/', status_code=200)
        self.assertContains(response, "Get started")

    def test_about_logged_out(self):
        response = self.client.get('/about/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Our story")

    def test_about_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/about/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Our story")

    def test_login(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login with Google")
        self.assertContains(response, "Login with Facebook")
        self.assertContains(response, "Login with Twitter")
        self.assertContains(response, "Forgot password")
        self.assertContains(response, "Sign up")

    def test_signup(self):
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign up with Google")
        self.assertContains(response, "Sign up with Facebook")
        self.assertContains(response, "Sign up with Twitter")
        self.assertContains(response, "Sign up")
        self.assertContains(response, "Sign in")

        data = {
            'email': 'mytestemail@gmail.com',
            'email2': 'mytestemail@gmail.com',
            'password1': 'mytestpassword1',
            'password2': 'mytestpassword1',
        }
        response = self.client.post('/accounts/signup/', data)
        self.assertRedirects(response, '/accounts/confirm-email/', 302, 200)

        user = User.objects.filter(email='mytestemail@gmail.com')
        self.assertEqual(len(user), 1)
        user = user[0]
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')
        self.assertEqual(user.userprofile.birthday, None)
        self.assertEqual(user.userprofile.state, '')
        self.assertEqual(user.email, data['email'])

    def test_social_signup(self):
        response = self.client.get('/accounts/social/signup/')
        self.assertRedirects(response, '/accounts/login/', 302, 200)

    def test_create_logged_out(self):
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create a Page")
        self.assertContains(response, "Create a Campaign")
        self.assertContains(response, "How it works")
        self.assertContains(response, "Select")
        self.assertContains(response, "Features")

    def test_create_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create a Page")
        self.assertContains(response, "Create a Campaign")
        self.assertContains(response, "How it works")
        self.assertContains(response, "Select")
        self.assertContains(response, "Features")

    def test_features_logged_out(self):
        response = self.client.get('/features/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nonprofit verification")
        self.assertContains(response, "Analytics")
        self.assertContains(response, "Campaigns")
        self.assertContains(response, "Share")

    def test_features_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/features/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nonprofit verification")
        self.assertContains(response, "Analytics")
        self.assertContains(response, "Campaigns")
        self.assertContains(response, "Share")

    def test_invite_logged_out(self):
        response = self.client.get('/invite/')

        self.assertRedirects(response, '/accounts/login/?next=/invite/', 302, 200)

    def test_invite_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/invite/')

        self.assertEqual(response.status_code, 200)

    def test_invite_accept_no_account(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/invite/')

        self.assertEqual(response.status_code, 200)
        response = self.client.post('/invite/', {'email': 'my@best.friend'})
        self.assertRedirects(response, '/', 302, 200)
        self.client.logout()

        response = self.client.get('/accounts/signup/')
        data = {
            'email': 'my@best.friend',
            'email2': 'my@best.friend',
            'password1': 'verybadpass5',
            'password2': 'verybadpass5',
        }
        response = self.client.post('/accounts/signup/', data)
        self.assertRedirects(response, '/accounts/confirm-email/', 302, 200)

        users = User.objects.all()
        user = User.objects.get(email='my@best.friend')
        self.assertIn(user, users)

    def test_invite_user_exists(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/invite/', {'email': 'another@guy.me'})

        self.assertRedirects(response, '/notes/error/invite/user-exists/', 302, 200)

    def test_forgot_password_request(self):
        response = self.client.get('/password/forgot/')
        self.assertEqual(response.status_code, 200)

    def test_change_password_request(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/password/change/')
        self.assertRedirects(response, '/profile/', 302, 200)

    def test_terms_of_service(self):
        response = self.client.get('/terms-of-service/')
        self.assertEqual(response.status_code, 200)

    def test_privacy_policy(self):
        response = self.client.get('/privacy-policy/')
        self.assertEqual(response.status_code, 200)

class AccountTests(TestCase):
    def _create_user(self, username='john', password='doe'):
        user = get_user_model().objects.create(
            username=username,
            is_active=True)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def _create_user_and_login(self, usable_password=True):
        password = 'doe' if usable_password else False
        user = self._create_user(password=password)
        c = self.client
        c.force_login(user)
        return user

#    def test_password_reset_get(self):
#        resp = self.client.get(reverse('account_reset_password'))
#        self.assertTemplateUsed(resp, 'password_reset.html')

    def _password_set_or_change_redirect(self, urlname, usable_password):
        self._create_user_and_login(usable_password)
        return self.client.get(reverse(urlname))

    def test_password_set_redirect(self):
        resp = self._password_set_or_change_redirect(
            'account_set_password',
            True)
        self.assertRedirects(
            resp,
            reverse('account_change_password'),
            fetch_redirect_response=False)

    def test_password_change_no_redirect(self):
        resp = self._password_set_or_change_redirect(
            'account_change_password',
            True)
        self.assertEqual(resp.status_code, 200)

    def test_password_set_no_redirect(self):
        resp = self._password_set_or_change_redirect(
            'account_set_password',
            False)
        self.assertEqual(resp.status_code, 200)

    def test_password_change_redirect(self):
        resp = self._password_set_or_change_redirect(
            'account_change_password',
            False)
        self.assertRedirects(
            resp,
            reverse('account_set_password'),
            fetch_redirect_response=False)

    def _request_new_password(self):
        user = get_user_model().objects.create(
            username='john', email='john@doe.org', is_active=True)
        user.set_password('doe')
        user.save()
        self.client.post(
            reverse('account_reset_password'),
            data={'email': 'john@doe.org'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['john@doe.org'])
        return user

    def _logout_view(self, method):
        c = Client()
        user = get_user_model().objects.create(username='john', is_active=True)
        user.set_password('doe')
        user.save()
        c = Client()
        c.login(username='john', password='doe')
        return c, getattr(c, method)(reverse('account_logout'))

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True)
    def test_logout_view_on_get(self):
        c, resp = self._logout_view('get')
        self.assertTemplateUsed(resp, 'account/messages/logged_out.txt')

    @override_settings(ACCOUNT_LOGOUT_ON_GET=False)
    def test_logout_view_on_post(self):
        c, resp = self._logout_view('get')
        self.assertTemplateUsed(
            resp,
            'account/logout.%s' % app_settings.TEMPLATE_EXTENSION)
        resp = c.post(reverse('account_logout'))
        self.assertTemplateUsed(resp, 'account/messages/logged_out.txt')

    @override_settings(ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=False)
    def test_account_authenticated_login_redirects_is_false(self):
        self._create_user_and_login()
        resp = self.client.get(reverse('account_login'))
        self.assertEqual(resp.status_code, 200)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
            }
        }])
    def test_django_password_validation(self):
        if django.VERSION < (1, 9, ):
            return
        resp = self.client.post(
            reverse('account_signup'),
            {'username': 'johndoe',
             'email': 'john@doe.com',
             'password1': 'johndoe',
             'password2': 'johndoe'})
        self.assertFormError(resp, 'form', None, [])
        self.assertFormError(
            resp,
            'form',
            'password1',
            ['Your password must be at least 7 characters and contain at least 1 number.'])


class BaseSignupFormTests(TestCase):
    @override_settings(ACCOUNT_USERNAME_REQUIRED=True)
    def test_username_maxlength(self):
        data = {
            'username': 'username',
            'email': 'user@example.com',
        }
        form = BaseSignupForm(data, email_required=True)
        max_length = get_username_max_length()
        field = form.fields['username']
        self.assertEqual(field.max_length, max_length)
        widget = field.widget
        self.assertEqual(widget.attrs.get('maxlength'), str(max_length))


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(
            is_active=True,
            email='john@doe.com',
            username='john')
        user.set_password(user.username)
        user.save()
        self.user = user

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME)  # noqa
    def test_auth_by_username(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username),
            None)

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL)  # noqa
    def test_auth_by_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username),
            None)

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME_EMAIL)  # noqa
    def test_auth_by_username_or_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username).pk,
            user.pk)
