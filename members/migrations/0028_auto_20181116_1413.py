# Generated by Django 2.0.2 on 2018-11-16 13:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0027_auto_20181019_2216'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommitteeMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='committee',
            name='leader_board',
        ),
        migrations.RemoveField(
            model_name='committee',
            name='leader_member',
        ),
        migrations.AddField(
            model_name='committee',
            name='leader',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leader_of', to=settings.AUTH_USER_MODEL, verbose_name='leder'),
        ),
        migrations.AddField(
            model_name='committee',
            name='leader_title',
            field=models.CharField(blank=True, max_length=100, verbose_name='ledertittel'),
        ),
        migrations.AddField(
            model_name='committeemembership',
            name='committee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.Committee'),
        ),
        migrations.AddField(
            model_name='committeemembership',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='committee',
            name='members',
            field=models.ManyToManyField(related_name='committees', through='members.CommitteeMembership', to=settings.AUTH_USER_MODEL, verbose_name='medlemmer'),
        ),
    ]
