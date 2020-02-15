from django.db import models


class Image(models.Model):
    path = models.CharField(max_length=200)
    width = models.IntegerField()
    height = models.IntegerField()


