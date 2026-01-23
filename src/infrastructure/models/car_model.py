from django.db import models


class CarModel(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    plate_number = models.CharField(max_length=20, unique=True, db_index=True)
    color = models.CharField(max_length=30)
    price_per_day = models.DecimalField(max_digits=12, decimal_places=2)
    regional = models.ForeignKey(
        "infrastructure.RegionalModel", on_delete=models.CASCADE, related_name="cars"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cars"
        indexes = [
            models.Index(fields=["regional", "created_at"]),
        ]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"
