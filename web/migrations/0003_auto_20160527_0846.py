# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-27 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20160527_0844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charts',
            name='chart_type',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='charts',
            name='y_name',
            field=models.CharField(max_length=30),
        ),
    ]
