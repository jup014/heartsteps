# Generated by Django 3.1.7 on 2021-04-16 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nlm', '0004_remove_cohortassignment_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conditionality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=1024)),
                ('module', models.CharField(max_length=1024)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
