# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-20 02:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('page', '0003_page_created_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='page',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='page',
            name='deleted_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
