# Generated by Django 2.1.1 on 2019-02-07 14:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='navn')),
                ('description', models.TextField(blank=True, default='', verbose_name='beskrivelse')),
                ('loaned_out', models.BooleanField(default=False)),
                ('loan_description', models.TextField(blank=True, default='', verbose_name='lånebeskrivelse')),
            ],
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('inventoryitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inventory.InventoryItem')),
            ],
            bases=('inventory.inventoryitem',),
        ),
        migrations.CreateModel(
            name='UniformPiece',
            fields=[
                ('inventoryitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inventory.InventoryItem')),
                ('size', models.CharField(max_length=30, verbose_name='størrelse')),
            ],
            bases=('inventory.inventoryitem',),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='loaned_to_member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='loaned_from', to=settings.AUTH_USER_MODEL, verbose_name='loaned_to'),
        ),
        migrations.CreateModel(
            name='Hat',
            fields=[
                ('uniformpiece_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inventory.UniformPiece')),
            ],
            bases=('inventory.uniformpiece',),
        ),
        migrations.CreateModel(
            name='Jacket',
            fields=[
                ('uniformpiece_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inventory.UniformPiece')),
                ('number', models.IntegerField(verbose_name='jakkenummer')),
            ],
            bases=('inventory.uniformpiece',),
        ),
        migrations.CreateModel(
            name='Pants',
            fields=[
                ('uniformpiece_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inventory.UniformPiece')),
            ],
            bases=('inventory.uniformpiece',),
        ),
    ]