from django.contrib.gis.db import models

class Library(models.Model):
    name = models.TextField()
    street = models.TextField(blank=True, null=True)
    postcode = models.TextField(blank=True, null=True)
    opening_hours = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    operator = models.TextField(blank=True, null=True)
    wheelchair = models.TextField(blank=True, null=True)
    geom = models.PointField()

    class Meta:
        db_table = 'libraries'  # ← this points Django to your existing table
