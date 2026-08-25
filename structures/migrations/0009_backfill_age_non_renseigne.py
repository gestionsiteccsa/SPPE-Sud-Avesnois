"""Marque les fiches sans tranche d'âge comme « âge non renseigné ».

Les structures sans âge minimum ni maximum (et sans case « âge non renseigné »
cochée) devenaient impossibles à modifier via le formulaire : la règle exige
désormais une tranche d'âge ou la case « âge non renseigné ».
"""

from django.db import migrations


def forward(apps, schema_editor):
    Structure = apps.get_model("structures", "Structure")
    Structure.objects.filter(
        age_non_renseigne=False,
        age_min__isnull=True,
        age_max__isnull=True,
    ).update(age_non_renseigne=True)


def reverse(apps, schema_editor):
    Structure = apps.get_model("structures", "Structure")
    Structure.objects.filter(
        age_non_renseigne=True,
        age_min__isnull=True,
        age_max__isnull=True,
    ).update(age_non_renseigne=False)


class Migration(migrations.Migration):

    dependencies = [
        ("structures", "0008_alter_structure_options_structure_nom_structure_and_more"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
