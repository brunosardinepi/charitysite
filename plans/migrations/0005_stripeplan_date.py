# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-23 13:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0004_auto_20171020_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripeplan',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
