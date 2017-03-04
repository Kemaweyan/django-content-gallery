from django.db import models

class Image(models.Model):
    src = models.ImageField()
    position = models.IntegerField()
