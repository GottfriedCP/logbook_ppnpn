# Generated by Django 5.1.7 on 2025-04-07 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logbook_ppnpn', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catatan',
            name='masalah_hambatan',
            field=models.TextField(blank=True, null=True, verbose_name='Masalah atau hambatan'),
        ),
        migrations.AlterField(
            model_name='catatan',
            name='tautan_dakung',
            field=models.URLField(blank=True, max_length=2000, null=True),
        ),
    ]
