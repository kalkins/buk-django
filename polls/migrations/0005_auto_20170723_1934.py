# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-23 17:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20170429_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='polloption',
            name='title',
            field=models.CharField(max_length=20, verbose_name='tittel'),
        ),
    ]
