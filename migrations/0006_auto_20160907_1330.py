# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-07 20:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('civic_calendar', '0005_entity_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entity',
            old_name='user',
            new_name='owner',
        ),
    ]