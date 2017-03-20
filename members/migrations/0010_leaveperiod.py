# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-19 21:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0009_auto_20170316_1319'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeavePeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(verbose_name='start')),
                ('end', models.DateField(blank=True, null=True, verbose_name='slutt')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_periods', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'permisjonsperioder',
                'verbose_name_plural': 'permisjonsperioder',
                'ordering': ['end', 'start'],
                'abstract': False,
            },
        ),
    ]