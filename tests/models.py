from django.db import models

class TestModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
