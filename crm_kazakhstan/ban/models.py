from mothers.models import Mother

from django.db import models


class Ban(models.Model):
    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    banned = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.mother}.ban instance'


class BanProxy(Mother):
    class Meta:
        verbose_name = 'banproxy'
        verbose_name_plural = 'banproxys'
        proxy = True
