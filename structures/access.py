from django.contrib.auth import get_user_model

from authentication.models import UserCommune

User = get_user_model()


def allowed_commune_ids(user: User) -> list[int] | None:
    """Communes accessibles pour un utilisateur ; None signifie toutes."""
    if user.is_superuser:
        return None
    return list(
        UserCommune.objects.filter(user=user).values_list("commune_id", flat=True)
    )
