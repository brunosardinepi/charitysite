# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-30 16:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0021_auto_20171128_0919'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='donation_count',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='donation_money',
        ),
    ]
