# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-02 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20170503_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='forum',
            field=models.CharField(choices=[('musikk', 'Musikk og noter'), ('diverse', 'Diverse'), ('styret', 'Styret')], default='diverse', max_length=2, verbose_name='forum'),
        ),
    ]
