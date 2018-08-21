# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-21 15:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('push_messages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageReciept',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('time', models.DateTimeField()),
                ('type', models.CharField(choices=[('recieved', 'Recieved'), ('opened', 'Opened'), ('closed', 'Closed')], max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='message',
            name='recieved',
        ),
        migrations.RemoveField(
            model_name='message',
            name='sent',
        ),
        migrations.AddField(
            model_name='messagereciept',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='push_messages.Message'),
        ),
    ]
