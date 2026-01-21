from django.db import models


class UserModel(models.Model):
    username = models.CharField(max_length=32, unique=True, db_index=True)
    password = models.TextField()  # TextField to accommodate various hashing algorithms
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username
