# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-25 01:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('civic_calendar', '0008_auto_20170123_1410'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set([('name', 'address', 'city')]),
        ),
    ]