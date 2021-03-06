# Generated by Django 2.0.2 on 2018-02-06 23:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0006_auto_20180128_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='poll',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='polls.Poll'),
        ),
        migrations.AlterField(
            model_name='post',
            name='poster',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
