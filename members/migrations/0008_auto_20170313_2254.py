# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 21:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0007_auto_20170313_1502'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(verbose_name='start')),
                ('end', models.DateField(null=True, verbose_name='slutt')),
            ],
            options={
                'verbose_name': 'periode',
                'verbose_name_plural': 'perioder',
                'ordering': ['end', 'start'],
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['instrument', '-is_active', 'group_leader_for', 'first_name', 'last_name'], 'verbose_name': 'medlem', 'verbose_name_plural': 'medlemmer'},
        ),
        migrations.RemoveField(
            model_name='member',
            name='joined_date',
        ),
        migrations.RemoveField(
            model_name='member',
            name='quit_date',
        ),
        migrations.AddField(
            model_name='membershipperiod',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_periods', to=settings.AUTH_USER_MODEL),
        ),
    ]