# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-05 03:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('campaign', '0001_initial'),
        ('page', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('anonymous_amount', models.BooleanField(default=False)),
                ('anonymous_donor', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('stripe_charge_id', models.CharField(blank=True, max_length=255)),
                ('donor_first_name', models.CharField(blank=True, max_length=255)),
                ('donor_last_name', models.CharField(blank=True, max_length=255)),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='campaign.Campaign')),
                ('campaign_participant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='campaign.VoteParticipant')),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='page.Page')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
