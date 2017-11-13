# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-13 21:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('archived', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('downvotes', models.IntegerField(default=0)),
                ('question', models.TextField()),
                ('upvotes', models.IntegerField(default=1)),
            ],
        ),
    ]
