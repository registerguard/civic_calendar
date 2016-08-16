# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-06 01:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('civic_calendar', '0003_auto_20160625_0317'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]