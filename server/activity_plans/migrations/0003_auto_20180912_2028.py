# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-12 20:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity_plans', '0002_auto_20180908_0124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitylog',
            name='type',
        ),
        migrations.RemoveField(
            model_name='activitylog',
            name='user',
        ),
        migrations.RemoveField(
            model_name='activitytype',
            name='user',
        ),
        migrations.AddField(
            model_name='activityplan',
            name='isComplete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='activityplan',
            name='log',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activity_logs.ActivityLog'),
        ),
        migrations.AlterField(
            model_name='activityplan',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity_logs.ActivityType'),
        ),
        migrations.DeleteModel(
            name='ActivityLog',
        ),
        migrations.DeleteModel(
            name='ActivityType',
        ),
    ]
