# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 14:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0006_auto_20170309_1950'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instrument',
            options={'ordering': ['order', 'name'], 'verbose_name': 'instrument', 'verbose_name_plural': 'instrumenter'},
        ),
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['instrument', 'is_active', 'group_leader_for', 'first_name'], 'verbose_name': 'medlem', 'verbose_name_plural': 'medlemmer'},
        ),
        migrations.AlterField(
            model_name='member',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='admin'),
        ),
    ]
