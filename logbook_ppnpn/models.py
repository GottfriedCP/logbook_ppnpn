from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Catatan(TimestampedModel):
    BIASA = "biasa"
    DISKUSI = "diskusi"
    KRITERIA_CHOICES = {
        BIASA: "Biasa",
        DISKUSI: "Perlu Diskusi",
    }

    nippnpn = models.CharField(max_length=20, null=False, blank=False)
    tanggal = models.DateField(blank=False, null=False)
    rincian = models.TextField()
    tautan_dakung = models.URLField(max_length=2000, null=True, blank=True)
    progress = models.TextField(blank=True, null=True)
    masalah_hambatan = models.TextField(
        blank=True, null=True, verbose_name="Masalah atau hambatan"
    )
    kriteria = models.CharField(choices=KRITERIA_CHOICES, default=BIASA, max_length=20)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["nippnpn", "-created_at"]
