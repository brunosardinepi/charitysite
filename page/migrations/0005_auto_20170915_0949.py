# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-15 14:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0004_auto_20170913_2146'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pageimages',
            old_name='is_cover',
            new_name='page_profile',
        ),
    ]
