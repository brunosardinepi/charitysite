# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-23 15:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0020_auto_20171023_1012'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PageImages',
            new_name='PageImage',
        ),
    ]