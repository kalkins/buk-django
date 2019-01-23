# Generated by Django 2.0.6 on 2018-12-28 23:03

from django.db import migrations, models
import django.db.models.deletion


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
        migrations.AlterField(
            model_name='member',
            name='percussion_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='members.PercussionGroup', verbose_name='slagverkgruppe'),
        ),
    ]
