# Generated by Django 2.0.2 on 2018-02-23 11:56

from django.db import migrations
from django.core.exceptions import ObjectDoesNotExist

# Django doesn't currently support creating child models from
# existing parent models, so we have a woraround. See this for details:
# https://code.djangoproject.com/ticket/7623#comment:20

def convert_boardposition_inheritance(apps, schema_editor):
    BoardPosition = apps.get_model('members', 'BoardPosition')
    Committee = apps.get_model('members', 'Committee')

    # Fetch all committees with leaders in the board
    # This must be done before altering foreign keys,
    # to avoid conflicts
    coms = {
        c.leader_board_id: c
        for c in Committee.objects.exclude(leader_board=None)
    }

    for pos in BoardPosition.objects.all():
        # The BoardPositions primary key will
        # change in this process, so any relationships
        # in other models must be updated
        com = coms[pos.pk] if pos.pk in coms else None

        parent_group = pos.group
        pos.inheritancegroup_ptr = parent_group
        pos.save()
        parent_group.save()

        # We have to refetch to update the attributes properly
        if com:
            com.leader_board_id = parent_group.pk
            com.save()


def convert_committee_inheritance(apps, schema_editor):
    Committee = apps.get_model('members', 'Committee')
    for com in Committee.objects.all():
        parent_group = com.group
        com.inheritancegroup_ptr = parent_group
        com.save()
        parent_group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0022_auto_20180223_1256'),
    ]

    operations = [
        migrations.RunPython(convert_boardposition_inheritance),
        migrations.RunPython(convert_committee_inheritance),
    ]
