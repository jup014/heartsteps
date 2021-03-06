# Generated by Django 3.1.7 on 2021-03-06 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomization', '0019_auto_20200727_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decision',
            name='available',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='decision',
            name='sedentary',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='decision',
            name='treated',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='decisionrating',
            name='liked',
            field=models.BooleanField(null=True),
        ),
    ]
