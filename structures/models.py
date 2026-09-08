from datetime import date
import re
import unicodedata

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from communes.models import Commune


class TypeStructure(models.Model):
    nom = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Type de structure"
        verbose_name_plural = "Types de structure"
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._audit_original = {
            f.name: f.value_from_object(instance) for f in cls._meta.fields
        }
        return instance


UNITE_AGE_CHOICES = [
    ("semaine", "semaine(s)"),
    ("mois", "mois"),
    ("ans", "an(s)"),
]

JOURS_SEM = [
    ("lundi", "Lundi"),
    ("mardi", "Mardi"),
    ("mercredi", "Mercredi"),
    ("jeudi", "Jeudi"),
    ("vendredi", "Vendredi"),
    ("samedi", "Samedi"),
    ("dimanche", "Dimanche"),
]


def horaires_default():
    return [{"jour": j[0], "ferme": True} for j in JOURS_SEM]


def _normaliser_pour_comparaison(value: str) -> str:
    """Minuscules, sans accents, ponctuation neutralisée : comparaison tolérante."""
    sans_accents = unicodedata.normalize("NFKD", value or "")
    sans_accents = sans_accents.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", sans_accents.lower()).strip()


class Structure(models.Model):
    reference_monenfant = models.BooleanField(default=True, verbose_name="Référencé monenfant.fr")
    date_mise_a_jour = models.DateField(auto_now=True, db_index=True, verbose_name="Date de mise à jour")
    date_mise_a_jour_monenfant = models.DateField(
        null=True, blank=True, db_index=True, verbose_name="Date mise à jour monenfant.fr"
    )
    latitude = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Longitude")
    afficher = models.BooleanField(default=True, verbose_name="Afficher sur le site")

    nom = models.CharField(max_length=255, blank=True, verbose_name="Nom")
    prenom = models.CharField(max_length=255, blank=True, verbose_name="Prénom")
    nom_structure = models.CharField(
        max_length=255, blank=True, verbose_name="Nom de la structure"
    )
    type = models.ForeignKey(
        TypeStructure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Type",
    )

    # Tranche d'âge
    age_non_renseigne = models.BooleanField(default=False, verbose_name="Âge non renseigné")
    age_min = models.IntegerField(null=True, blank=True, verbose_name="Âge minimum")
    age_min_unite = models.CharField(
        max_length=10, choices=UNITE_AGE_CHOICES, blank=True, verbose_name="Unité âge min"
    )
    age_max = models.IntegerField(null=True, blank=True, verbose_name="Âge maximum")
    age_max_unite = models.CharField(
        max_length=10, choices=UNITE_AGE_CHOICES, blank=True, verbose_name="Unité âge max"
    )

    # Horaires
    horaires = models.JSONField(
        default=horaires_default, verbose_name="Horaires par jour"
    )
    horaires_notes = models.TextField(blank=True, verbose_name="Notes horaires")

    # Adresse
    commune = models.ForeignKey(
        Commune, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Commune"
    )
    adresse = models.CharField(max_length=255, blank=True, verbose_name="Adresse")

    # Contact
    telephone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")

    # Places
    places_disponibles = models.IntegerField(null=True, blank=True, verbose_name="Places disponibles")
    places_complet = models.BooleanField(default=False, verbose_name="Complet")
    places_non_communique = models.BooleanField(default=False, verbose_name="Non communiqué")
    conditions_places = models.TextField(blank=True, verbose_name="Conditions places disponibles")
    nb_places_total = models.IntegerField(null=True, blank=True, verbose_name="Nombre de places total")

    # Infos complémentaires
    accueil_handicap = models.BooleanField(null=True, blank=True, verbose_name="Accueil handicap")
    site_web = models.URLField(blank=True, verbose_name="Site web")
    directeur = models.CharField(max_length=255, blank=True, verbose_name="Directeur/trice")
    tel_direction = models.CharField(max_length=50, blank=True, verbose_name="Tél. direction")
    email_direction = models.EmailField(blank=True, verbose_name="Email direction")
    statut = models.CharField(max_length=100, blank=True, verbose_name="Statut")
    aides = models.CharField(max_length=255, blank=True, verbose_name="Aides")
    nb_professionnels = models.IntegerField(null=True, blank=True, verbose_name="Nb professionnel·les")
    recrutement = models.BooleanField(null=True, blank=True, verbose_name="Recrutement en cours")
    accueil_urgence = models.BooleanField(null=True, blank=True, verbose_name="Accueil d'urgence")

    class Meta:
        verbose_name = "Structure"
        verbose_name_plural = "Structures"
        ordering = ["nom_structure", "nom", "prenom"]
        indexes = [
            models.Index(
                fields=["afficher", "date_mise_a_jour"],
                name="structure_visible_recent",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(places_disponibles__isnull=True)
                | models.Q(places_disponibles__gte=0),
                name="structure_places_disponibles_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(nb_places_total__isnull=True)
                | models.Q(nb_places_total__gte=0),
                name="structure_places_total_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(nb_professionnels__isnull=True)
                | models.Q(nb_professionnels__gte=0),
                name="structure_professionnels_positifs",
            ),
            models.CheckConstraint(
                condition=models.Q(age_min__isnull=True) | models.Q(age_min__gte=0),
                name="structure_age_min_positif",
            ),
            models.CheckConstraint(
                condition=models.Q(age_max__isnull=True) | models.Q(age_max__gte=0),
                name="structure_age_max_positif",
            ),
            models.CheckConstraint(
                condition=~models.Q(places_complet=True, places_non_communique=True),
                name="structure_places_statuts_coherents",
            ),
            models.CheckConstraint(
                condition=models.Q(places_disponibles__isnull=True)
                | models.Q(nb_places_total__isnull=True)
                | models.Q(places_disponibles__lte=models.F("nb_places_total")),
                name="structure_places_disponibles_lte_total",
            ),
        ]

    def __str__(self):
        return self.nom_affiche

    @property
    def nom_affiche(self):
        if self.nom_structure.strip():
            return self.nom_structure
        return " ".join(part for part in (self.prenom, self.nom) if part.strip()) or self.nom

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._audit_original = {
            f.name: f.value_from_object(instance) for f in cls._meta.fields
        }
        return instance

    def clean(self):
        super().clean()
        errors = {}
        has_structure_name = bool(self.nom_structure.strip())
        has_individual_name = bool(self.nom.strip()) or bool(self.prenom.strip())
        if has_structure_name and has_individual_name:
            errors["nom_structure"] = (
                "Choisissez un nom de structure ou un nom/prénom, pas les deux."
            )
        if self.age_non_renseigne and (
            self.age_min is not None or self.age_max is not None
        ):
            errors["age_non_renseigne"] = (
                "Une tranche d'âge ne peut pas être renseignée lorsque l'âge est déclaré inconnu."
            )
        if not self.age_non_renseigne and (
            self.age_min is None or self.age_max is None
        ):
            errors["age_non_renseigne"] = (
                "Renseignez la tranche d'âge (âge minimum et âge maximum) "
                "ou cochez « Âge non renseigné »."
            )
        for value_field, unit_field in (
            ("age_min", "age_min_unite"),
            ("age_max", "age_max_unite"),
        ):
            value = getattr(self, value_field)
            unit = getattr(self, unit_field)
            if value is not None and not unit:
                errors[unit_field] = "L'unité est obligatoire lorsque l'âge est renseigné."
            elif value is None and unit:
                errors[value_field] = "L'âge est obligatoire lorsqu'une unité est sélectionnée."
        if (
            self.age_min is not None
            and self.age_max is not None
            and self.age_min_unite
            and self.age_max_unite
        ):
            weeks_per_unit = {"semaine": 1, "mois": 4.35, "ans": 52}
            minimum_factor = weeks_per_unit.get(self.age_min_unite)
            maximum_factor = weeks_per_unit.get(self.age_max_unite)
            if (
                minimum_factor is not None
                and maximum_factor is not None
                and self.age_min * minimum_factor > self.age_max * maximum_factor
            ):
                errors["age_max"] = "L'âge maximum doit être supérieur ou égal à l'âge minimum."
        if self.places_complet and self.places_non_communique:
            errors["places_complet"] = "Une structure ne peut pas être à la fois complète et non communiquée."
        if (
            self.places_disponibles is not None
            and self.nb_places_total is not None
            and self.places_disponibles > self.nb_places_total
        ):
            errors["places_disponibles"] = (
                "Le nombre de places disponibles ne peut pas dépasser la capacité totale."
            )
        if errors:
            raise ValidationError(errors)

    def afficher_age(self):
        if self.age_non_renseigne:
            return "Non renseigné"
        parties = []
        if self.age_min is not None and self.age_min_unite:
            parties.append(f"{self.age_min} {self.age_min_unite}")
        if self.age_max is not None and self.age_max_unite:
            parties.append(f"{self.age_max} {self.age_max_unite}")
        return " - ".join(parties) if parties else "Non renseigné"

    @property
    def adresse_affichee(self):
        """Adresse postale sans doublon de commune/code postal.

        Les adresses saisies via la BAN contiennent déjà « CP Ville » ; dans
        ce cas on affiche l'adresse telle quelle, sinon on ajoute le suffixe
        « CP Ville » (comparaison insensible à la casse et aux accents).
        """
        adresse = (self.adresse or "").strip()
        suffixe = ""
        if self.commune:
            suffixe = " ".join(
                part
                for part in (self.commune.code_postal, self.commune.nom)
                if (part or "").strip()
            )
        if adresse and suffixe:
            if _normaliser_pour_comparaison(suffixe) in _normaliser_pour_comparaison(adresse):
                return adresse
            return f"{adresse}, {suffixe}"
        return adresse or suffixe

    def afficher_horaires(self):
        if not self.horaires:
            return ""
        jours = {j[0]: j[1] for j in JOURS_SEM}
        lignes = []
        for entry in self.horaires:
            jour = jours.get(entry.get("jour", ""), entry.get("jour", ""))
            if entry.get("ferme"):
                lignes.append(f"{jour}: fermé")
            else:
                ouverture = entry.get("ouverture", "")
                fermeture = entry.get("fermeture", "")
                lignes.append(f"{jour} {ouverture}-{fermeture}")
        txt = ", ".join(lignes)
        if self.horaires_notes:
            txt += f" ({self.horaires_notes})"
        return txt

    def afficher_places(self):
        if self.places_non_communique:
            return "Non communiqué"
        if self.places_complet:
            return "Complet"
        if self.places_disponibles is not None:
            return str(self.places_disponibles)
        return "Non communiqué"

    def monenfant_status(self):
        if not self.date_mise_a_jour_monenfant:
            return ("neutral", "—")
        delta = date.today() - self.date_mise_a_jour_monenfant
        years = delta.days / 365.25
        if years < 1:
            return ("success", self.date_mise_a_jour_monenfant.strftime("%d/%m/%Y"))
        elif years < 2:
            return ("warning", self.date_mise_a_jour_monenfant.strftime("%d/%m/%Y"))
        else:
            return ("danger", self.date_mise_a_jour_monenfant.strftime("%d/%m/%Y"))

    def afficher_handicap(self):
        if self.accueil_handicap is None:
            return "Non concerné"
        return "Oui" if self.accueil_handicap else "Non"

    def afficher_urgence(self):
        if self.accueil_urgence is None:
            return "Non concerné"
        return "Oui" if self.accueil_urgence else "Non"

    def afficher_recrutement(self):
        if self.recrutement is None:
            return ""
        return "Oui" if self.recrutement else "Non"


AUDIT_ACTIONS = [
    ("create", "Création"),
    ("update", "Modification"),
    ("delete", "Suppression"),
    ("batch", "Action groupée"),
    ("import", "Import"),
]


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name="Utilisateur")
    action = models.CharField(max_length=20, choices=AUDIT_ACTIONS, verbose_name="Action")
    model_name = models.CharField(max_length=50, verbose_name="Modèle")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID objet")
    object_repr = models.CharField(max_length=255, blank=True, verbose_name="Représentation")
    changes = models.JSONField(default=dict, blank=True, verbose_name="Modifications")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal d'activité"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"], name="structures_auditlog_timestamp"),
        ]

    def __str__(self):
        return f"[{self.get_action_display()}] {self.model_name} #{self.object_id} — {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
