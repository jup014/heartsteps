# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-25 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_api', '0010_auto_20181018_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitbitdailystepsunprocessed',
            name='timezone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
