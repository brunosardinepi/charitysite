from collections import OrderedDict

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from comments.models import Comment
from donation.models import Donation
from pagefund import config


class Campaign(models.Model):
    campaign_admins = models.ManyToManyField('userprofile.UserProfile', related_name='campaign_admins', blank=True)
    campaign_managers = models.ManyToManyField('userprofile.UserProfile', related_name='campaign_managers', blank=True)
    campaign_slug = models.SlugField(max_length=255)
    city = models.CharField(max_length=255, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    deleted_on = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    donation_count = models.IntegerField(default=0)
    donation_money = models.IntegerField(default=0)
    goal = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=255, db_index=True)
    page = models.ForeignKey('page.Page', on_delete=models.CASCADE, related_name='campaigns')
    trending_score = models.DecimalField(default=0, max_digits=10, decimal_places=1)

    TYPE_CHOICES = (
        ('event', 'Event'),
    )
    type = models.CharField(
        max_length=255,
        choices=TYPE_CHOICES,
        default='Event',
    )

    STATE_CHOICES = (
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'),
    )
    state = models.CharField(
        max_length=100,
        choices=STATE_CHOICES,
        default='',
    )

    class Meta:
        permissions = (
            ('manager_edit', 'Manager -- edit Campaign'),
            ('manager_delete', 'Manager -- delete Campaign'),
            ('manager_invite', 'Manager -- invite users to manage Campaign'),
            ('manager_image_edit', 'Manager -- upload media to Campaign'),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('campaign', kwargs={
            'page_slug': self.page.page_slug,
            'campaign_pk': self.pk,
            'campaign_slug': self.campaign_slug
            })

    def save(self, *args, **kwargs):
        if self.id:
            self.campaign_slug = slugify(self.campaign_slug)
            super(Campaign, self).save(*args, **kwargs)
        elif not self.id:
            self.campaign_slug = slugify(self.name)
            super(Campaign, self).save(*args, **kwargs)

    def top_donors(self):
        donors = Donation.objects.filter(campaign=self).values_list('user', flat=True).distinct()
        top_donors = {}
        for d in donors:
            user = get_object_or_404(User, pk=d)
            total_amount = Donation.objects.filter(user=user, campaign=self, anonymous_amount=False, anonymous_donor=False).aggregate(Sum('amount')).get('amount__sum')
            if total_amount is not None:
                top_donors[d] = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'amount': total_amount
                }
        top_donors = OrderedDict(sorted(top_donors.items(), key=lambda t: t[1]['amount'], reverse=True))
        top_donors = list(top_donors.items())[:10]
        return top_donors

    def images(self):
        return CampaignImage.objects.filter(campaign=self)

    def profile_image(self):
        try:
            return CampaignImage.objects.get(campaign=self, campaign_profile=True)
        except CampaignImage.MultipleObjectsReturned:
            # create an exception for future use
            print("multiple profile images returned")

    def donations(self):
        return Donation.objects.filter(campaign=self).order_by('-date')

    def managers_list(self):
        return self.campaign_managers.all()

    def comments(self):
        return Comment.objects.filter(campaign=self, deleted=False).order_by('-date')


class CampaignImage(models.Model):
    campaign = models.ForeignKey('campaign.Campaign', on_delete=models.CASCADE)
    image = models.FileField(upload_to='media/campaigns/images/', blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True)
    campaign_profile = models.BooleanField(default=False)
