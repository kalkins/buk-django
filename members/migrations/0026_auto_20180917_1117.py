# Generated by Django 2.0.2 on 2018-09-17 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0025_auto_20180302_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inheritancegroup',
            name='own_permissions',
            field=models.ManyToManyField(blank=True, to='auth.Permission', verbose_name='Rettigheter'),
        ),
        migrations.AlterField(
            model_name='inheritancegroup',
            name='parents',
            field=models.ManyToManyField(blank=True, related_name='sub_groups', to='members.InheritanceGroup', verbose_name='Overgrupper'),
        ),
    ]
