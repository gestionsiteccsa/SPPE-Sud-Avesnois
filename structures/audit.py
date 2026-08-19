from contextlib import contextmanager
from contextvars import ContextVar
from collections.abc import Iterator

from django.contrib.auth.base_user import AbstractBaseUser


_CURRENT_ACTOR: ContextVar[AbstractBaseUser | None] = ContextVar(
    "structures_audit_actor",
    default=None,
)


def get_audit_actor() -> AbstractBaseUser | None:
    """Retourne l'acteur associé à l'opération métier courante."""
    return _CURRENT_ACTOR.get()


@contextmanager
def audit_actor(actor: AbstractBaseUser | None) -> Iterator[None]:
    """Associe temporairement un utilisateur aux signaux d'audit."""
    token = _CURRENT_ACTOR.set(actor)
    try:
        yield
    finally:
        _CURRENT_ACTOR.reset(token)
