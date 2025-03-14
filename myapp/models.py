from django.db import models

class Table(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data = models.JSONField(default=list)

    def __str__(self):
        return self.name

