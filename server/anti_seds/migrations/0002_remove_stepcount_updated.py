# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-11-13 23:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anti_seds', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stepcount',
            name='updated',
        ),
    ]
