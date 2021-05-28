# Generated by Django 3.1.7 on 2021-05-27 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nlm', '0003_auto_20210527_0220'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='logcontents',
            index=models.Index(fields=['-logtime', 'subject'], name='nlm_logcont_logtime_8eff8c_idx'),
        ),
    ]
