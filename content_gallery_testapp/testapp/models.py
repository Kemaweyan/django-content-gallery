from django.db import models

class Cat(models.Model):

    SEX_CHOICES = {
        ('M', "Male"),
        ('F', "Female")
    }

    name = models.CharField(max_length=50)
    age = models.IntegerField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
