# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-31 22:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('civic_calendar', '0010_auto_20170531_1545'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='entity',
            unique_together=set([('name', 'owner', 'jurisdiction')]),
        ),
    ]
