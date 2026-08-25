from contextlib import contextmanager
from contextvars import ContextVar
from django.db.models.signals import post_delete, post_save, pre_save

from campagnes.models import UpdateCampaign, UpdateRequest, UpdateRequestField, VerificationInvitation
from communes.models import Commune
from structures.audit import get_audit_actor
from structures.models import AuditLog, Structure, TypeStructure

AUDITED_MODELS = (
    Structure,
    TypeStructure,
    Commune,
    UpdateCampaign,
    VerificationInvitation,
    UpdateRequest,
    UpdateRequestField,
)
SKIP_FIELDS = {"date_mise_a_jour"}

_AUDIT_SUSPENDED: ContextVar[bool] = ContextVar(
    "structures_audit_suspended",
    default=False,
)


@contextmanager
def suspended_audit():
    """Suspend les signaux d'audit (opérations groupées : remplacement d'import…).

    Les écritures réalisées dans ce bloc ne génèrent aucune entrée de journal ;
    l'appelant reste responsable de consigner lui-même une entrée résumée.
    """
    token = _AUDIT_SUSPENDED.set(True)
    try:
        yield
    finally:
        _AUDIT_SUSPENDED.reset(token)


def _audit_value(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def _get_changes(old_values, instance):
    changes = {}
    for field in instance._meta.fields:
        name = field.name
        if name in SKIP_FIELDS:
            continue
        old_val = old_values.get(name)
        new_val = field.value_from_object(instance)
        if old_val != new_val:
            changes[name] = {
                "old": _audit_value(old_val),
                "new": _audit_value(new_val),
            }
    return changes


def _get_original(instance):
    original = getattr(instance, "_audit_original", None)
    if original is not None:
        return original
    if not instance.pk:
        return None
    old = instance.__class__.objects.filter(pk=instance.pk).first()
    if old is None:
        return None
    return {f.name: f.value_from_object(old) for f in instance._meta.fields}


def capture_changes(sender, instance, raw=False, **kwargs):
    if raw or _AUDIT_SUSPENDED.get():
        return
    original = _get_original(instance)
    instance._audit_changes = (
        _get_changes(original, instance) if original is not None else {"_created": True}
    )


def log_save(sender, instance, created=False, raw=False, **kwargs):
    if raw or _AUDIT_SUSPENDED.get():
        return
    user = get_audit_actor()
    changes = getattr(instance, "_audit_changes", {"_created": True} if created else {})
    if not changes and not created:
        return
    AuditLog.objects.create(
        user=user,
        action="create" if created else "update",
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        changes=changes,
    )


def log_delete(sender, instance, **kwargs):
    if _AUDIT_SUSPENDED.get():
        return
    AuditLog.objects.create(
        user=get_audit_actor(),
        action="delete",
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        changes={"_deleted": True},
    )


for _model in AUDITED_MODELS:
    pre_save.connect(capture_changes, sender=_model)
    post_save.connect(log_save, sender=_model)
    post_delete.connect(log_delete, sender=_model)
