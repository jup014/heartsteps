# Generated by Django 3.1.7 on 2021-04-16 15:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nlm', '0006_auto_20210416_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='conditionality',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='conditionality',
            unique_together={('name', 'user')},
        ),
    ]
