# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-09 09:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20170224_2323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='member',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='member',
            name='username',
        ),
    ]
