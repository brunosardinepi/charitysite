from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from page.models import Page
from userprofile.models import UserProfile

from pagefund import config

class Campaign(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    campaign_slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    goal = models.IntegerField(default=0)
    donation_count = models.IntegerField(default=0)
    donation_money = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    page = models.ForeignKey('page.Page', on_delete=models.CASCADE, related_name='campaigns')
    campaign_admins = models.ManyToManyField(UserProfile, related_name='campaign_admins', blank=True)
    campaign_managers = models.ManyToManyField(UserProfile, related_name='campaign_managers', blank=True)
    campaign_icon = models.ImageField(upload_to='media/campaigns/', blank=True, null=True)
    city = models.CharField(max_length=255, blank=True)
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
