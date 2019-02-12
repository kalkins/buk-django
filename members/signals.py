from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver

from .models import InheritanceGroup, Committee


@receiver(m2m_changed, sender=InheritanceGroup.parents.through)
@receiver(m2m_changed, sender=InheritanceGroup.own_permissions.through)
def update_permissions(sender, instance, action, reverse, **kwargs):
    if not reverse and action in ['post_add', 'post_remove', 'post_clear']:
        instance.update_permissions()


@receiver(post_save, sender=Committee.members.through)
@receiver(post_delete, sender=Committee.members.through)
@receiver(post_save, sender=Committee)
def update_committee_members(sender, instance, **kwargs):
    committee = instance if isinstance(instance, Committee) else instance.committee

    members = list(committee.members.all())
    if committee.leader:
        members.append(committee.leader)

    committee.user_set.set(members)
