# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-11 01:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='ICON_FOUND',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='ICON_HIDDEN',
            field=models.BooleanField(default=False),
        ),
    ]
