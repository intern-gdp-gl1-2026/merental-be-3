from django.db import models


class RegionalModel(models.Model):
    name = models.CharField(max_length=32, unique=True, db_index=True)

    class Meta:
        db_table = "regionals"

    def __str__(self):
        return self.name
