# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-09 18:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_auto_20170309_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='origin',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='kommer fra'),
        ),
    ]