# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-18 23:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0030_auto_20171218_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='page_slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
    ]
