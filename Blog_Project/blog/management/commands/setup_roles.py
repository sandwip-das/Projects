from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import Post, Comment

class Command(BaseCommand):
    help = 'Setup User Roles (Editor, Reader)'

    def handle(self, *args, **kwargs):
        # 1. Editor Group
        editor_group, created = Group.objects.get_or_create(name='Editor')
        
        perms_to_add = [
            ('add_post', Post),
            ('change_post', Post),
            ('delete_post', Post),
            ('change_comment', Comment),
            ('delete_comment', Comment),
        ]

        for codename, model in perms_to_add:
            ct = ContentType.objects.get_for_model(model)
            try:
                perm = Permission.objects.get(content_type=ct, codename=codename)
                editor_group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass # Already logged or irrelevant

        self.stdout.write(self.style.SUCCESS('Editor Group configured.'))

        # 2. Reader Group
        # Rename "Registered User" if it exists
        try:
            old_group = Group.objects.get(name='Registered User')
            old_group.name = 'Reader'
            old_group.save()
            self.stdout.write(self.style.SUCCESS('Renamed "Registered User" to "Reader".'))
        except Group.DoesNotExist:
            pass

        reader_group, created = Group.objects.get_or_create(name='Reader')
        self.stdout.write(self.style.SUCCESS('Reader Group configured.'))
