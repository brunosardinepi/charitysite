from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import config
from . import views
from campaign import views as CampaignViews
from invitations import views as InvitationsViews
from page import views as PageViews


urlpatterns = [
    url(r'^{}/'.format(config.settings['admin']), admin.site.urls),
    url(r'^accounts/login/', views.LoginView.as_view(), name='login'),
    url(r'^accounts/signup/', views.SignupView.as_view(), name='signup'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^profile/', include('userprofile.urls', namespace='userprofile')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^invite/$', views.invite, name='invite'),
    url(r'^invite/', include('invitations.urls', namespace='invitations')),
    url(r'^comments/', include('comments.urls', namespace='comments')),
    url(r'^donation/', include('donation.urls', namespace='donation')),
    url(r'^forgot/$', InvitationsViews.forgot_password_request, name='forgot_password_request'),
    url(r'^password/reset/(?P<invitation_pk>\d+)/(?P<key>[\w-]+)/$', InvitationsViews.forgot_password_reset, name='forgot_password_reset'),
    url(r'^webhooks/', include('webhooks.urls', namespace='webhooks')),
    url(r'^plans/', include('plans.urls', namespace='plans')),
    url(r'^faq/', include('faqs.urls', namespace='faqs')),
    url(r'^about/$', TemplateView.as_view(template_name="about.html")),
    url(r'^terms-of-service/$', TemplateView.as_view(template_name="terms_of_service.html")),
    url(r'^privacy-policy/$', TemplateView.as_view(template_name="privacy_policy.html")),
    url(r'^notes/', include('notes.urls', namespace='notes')),

    url(r'^page/subscribe/(?P<page_pk>\d+)/(?P<action>[\w-]*)/$', PageViews.subscribe, name='subscribe'),
    url(r'^create/$', PageViews.page_create, name='page_create'),
    url(r'^create/(?P<page_slug>[\w-]+)/additional/$', login_required(PageViews.PageCreateAdditionalInfo.as_view()), name='page_create_additional_info'),
    url(r'^create/(?P<page_slug>[\w-]+)/bank/$', login_required(PageViews.PageCreateBankInfo.as_view()), name='page_create_bank_info'),
    url(r'^(?P<page_slug>[\w-]+)/edit/bank/$', login_required(PageViews.PageEditBankInfo.as_view()), name='page_edit_bank_info'),
    url(r'^(?P<page_slug>[\w-]+)/edit/$', PageViews.page_edit, name='page_edit'),
    url(r'^(?P<page_slug>[\w-]+)/dashboard/$', login_required(PageViews.PageDashboard.as_view()), name='page_dashboard'),
    url(r'^page/dashboard/ajax/donations/', PageViews.PageAjaxDonations.as_view(), name='page_ajax_donations'),
    url(r'^(?P<page_slug>[\w-]+)/delete/$', PageViews.page_delete, name='page_delete'),
    url(r'^(?P<page_slug>[\w-]+)/donate/$', PageViews.PageDonate.as_view(), name='page_donate'),
    url(r'^(?P<page_slug>[\w-]+)/images/$', login_required(PageViews.PageImageUpload.as_view()), name='page_image_upload'),
    url(r'^page/image/(?P<image_pk>\d+)/delete/$', PageViews.page_image_delete, name='page_image_delete'),
    url(r'^page/image/(?P<image_pk>\d+)/profile-picture/$', PageViews.page_profile_update, name='page_profile_update'),
    url(r'^(?P<page_slug>[\w-]+)/managers/invite/$', PageViews.page_invite, name='page_invite'),
    url(r'^(?P<page_slug>[\w-]+)/managers/(?P<manager_pk>\d+)/remove/$', PageViews.remove_manager, name='remove_manager'),
    url(r'^(?P<page_slug>[\w-]+)/$', PageViews.page, name='page'),

    url(r'^campaign/subscribe/(?P<campaign_pk>\d+)/(?P<action>[\w-]*)/$', CampaignViews.subscribe, name='campaign_subscribe'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/donate/(?P<vote_participant_pk>\d+)/$', CampaignViews.CampaignDonate.as_view(), name='campaign_donate'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/donate/$', CampaignViews.CampaignDonate.as_view(), name='campaign_donate'),
    url(r'^campaign/create/$', login_required(CampaignViews.CampaignCreate.as_view()), name='campaign_create'),
    url(r'^campaign/create/search/$', CampaignViews.campaign_search_pages, name='campaign_search_pages'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/vote/edit/$', login_required(CampaignViews.CampaignEditVote.as_view()), name='campaign_edit_vote'),
    url(r'^(?P<page_slug>[\w-]+)/campaign/create/$', login_required(CampaignViews.CampaignCreate.as_view()), name='campaign_create'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/edit/$', CampaignViews.campaign_edit, name='campaign_edit'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/delete/$', CampaignViews.campaign_delete, name='campaign_delete'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/dashboard/$', login_required(CampaignViews.CampaignDashboard.as_view()), name='campaign_dashboard'),
    url(r'^campaign/dashboard/ajax/donations/', CampaignViews.CampaignAjaxDonations.as_view(), name='campaign_ajax_donations'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/images/$', login_required(CampaignViews.CampaignImageUpload.as_view()), name='campaign_image_upload'),
    url(r'^campaign/image/(?P<image_pk>\d+)/delete/$', CampaignViews.campaign_image_delete, name='campaign_image_delete'),
    url(r'^campaign/image/(?P<image_pk>\d+)/profile-picture/$', CampaignViews.campaign_profile_update, name='campaign_profile_update'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/managers/invite/$', CampaignViews.campaign_invite, name='campaign_invite'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/managers/(?P<manager_pk>\d+)/remove/$', CampaignViews.remove_manager, name='remove_manager'),
    url(r'^(?P<page_slug>[\w-]+)/(?P<campaign_pk>\d+)/(?P<campaign_slug>[\w-]+)/$', CampaignViews.campaign, name='campaign'),

    url(r'^$', views.home, name='home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
