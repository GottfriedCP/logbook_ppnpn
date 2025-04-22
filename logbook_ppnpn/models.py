from django.db import models
from django.utils import timezone


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
    tautan_dakung = models.URLField(
        max_length=2000,
        null=True,
        blank=True,
        verbose_name="Link Data Dukung",
    )
    progress = models.TextField(blank=True, null=True, verbose_name="Progress")
    masalah_hambatan = models.TextField(
        blank=True, null=True, verbose_name="Masalah atau hambatan"
    )
    kriteria = models.CharField(choices=KRITERIA_CHOICES, default=BIASA, max_length=20)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["nippnpn", "-created_at"]

    def verifikasi(self, *args, **kwargs):
        """Tandai catatan ini sudah diverifikasi."""
        self.verified = True
        self.verified_at = timezone.now()
        super().save(*args, **kwargs)

    def unverifikasi(self, *args, **kwargs):
        """Tandai catatan ini belum diverifikasi."""
        self.verified = False
        self.verified_at = None
        super().save(*args, **kwargs)
