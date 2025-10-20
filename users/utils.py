import re
from typing import List

from django.contrib.auth.models import Group, Permission


class CustomPasswordValidator:
    @staticmethod
    def validate(password: str):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()-+]).{8,}$', password):
            return f"Le mot de passe doit contenir au moins 8 caractères, une lettre majuscule, une lettre minuscule, un chiffre et un symbole.",

    def get_help_text(self):
        return "Votre mot de passe doit contenir au moins 8 caractères, une lettre majuscule, une lettre minuscule, un chiffre et un symbole."

def create_or_group_and_permission(name:str,permis:List[str]=None)->Group:

    group = Group.objects.get_or_create(name=name)

    # Ajouter des permissions spécifiques

    #permissions = Permission.objects.filter(codename__in=permis)
    #group = group[0]
    #group.permissions.set(permissions)
    #group.save()

    return group[0]
