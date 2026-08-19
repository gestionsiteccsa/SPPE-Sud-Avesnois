from django.db import models


class Commune(models.Model):
    nom = models.CharField(max_length=255)
    code_postal = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
        ordering = ["nom"]

    def __str__(self):
        return f"{self.code_postal} {self.nom}"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._audit_original = {
            f.name: f.value_from_object(instance) for f in cls._meta.fields
        }
        return instance
