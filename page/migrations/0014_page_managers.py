# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 21:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_auto_20170818_1521'),
        ('page', '0013_auto_20170822_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='managers',
            field=models.ManyToManyField(blank=True, related_name='managers', to='userprofile.UserProfile'),
        ),
    ]
