# Generated by Django 2.0.2 on 2018-10-20 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_auto_20181019_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='description',
            field=models.TextField(blank=True, verbose_name='beskrivelse'),
        ),
    ]