# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-02-11 17:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomization', '0010_auto_20190112_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='unavailable_reason',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
