from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role
from django.contrib.auth.models import Permission


@receiver(post_migrate)
def create_roles_and_assign_permissions(sender, **kwargs):
    if sender.name == 'rbac':
        staff_role, _ = Role.objects.get_or_create(name="Staff")
        staff_permissions = [
            'Can delete role',
            'Can add role',
            'Can change role',
            'Can view role',
        ]
        


        for perm in staff_permissions:
            permission = Permission.objects.filter(name=perm).first()
            if permission:
                print(permission)
                staff_role.permissions.add(permission)

        # Create user role
        user_role, _ = Role.objects.get_or_create(name="User")

        user_permissions = [
        ]

        for perm in user_permissions:
            permission = Permission.objects.filter(name=perm).first()
            if permission:
                print(permission)
                user_role.permissions.add(permission)
