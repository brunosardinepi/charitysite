# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-27 03:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='anonymous',
            field=models.BooleanField(default=False),
        ),
    ]