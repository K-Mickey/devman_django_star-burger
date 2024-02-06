from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Location(models.Model):
    latitude = models.FloatField(
        verbose_name='Широта',
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        verbose_name='Долгота',
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    address = models. CharField(
        verbose_name='Адрес',
        max_length=255,
        unique=True,
    )

    @property
    def coordinates(self):
        return self.longitude, self.latitude
