# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-03-13 18:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_activity_logs', '0003_auto_20190228_0054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitbitactivitytoactivitytype',
            name='fitbit_activity_type',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='fitbit_activities.FitbitActivityType'),
        ),
    ]
