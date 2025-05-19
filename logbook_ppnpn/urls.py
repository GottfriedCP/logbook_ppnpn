from django.urls import path

from . import views

app_name = "logbook_ppnpn"

urlpatterns = [
    path("", views.home, name="home"),
    # path("catatan-modal/", views.tampilkan_modal, name="catatan_modal"),
    path("buat-catatan/", views.buat_catatan, name="buat_catatan"),
    path("ubah-catatan/<int:id_catatan>/", views.ubah_catatan, name="ubah_catatan"),
    path("hapus-catatan/<int:id_catatan>/", views.hapus_catatan, name="hapus_catatan"),
    path("cetak-logbook/", views.cetak_logbook, name="cetak_logbook"),
    path("semua-logbook/<int:id_ppnpn>/", views.detail_logbook, name="detail_logbook"),
    path("semua-logbook/", views.semua_logbook, name="semua_logbook"),
    path("daftar-validasi/", views.list_validasi, name="list_validasi"),
    path("validasi/<int:id_catatan>/", views.validasi, name="validasi"),
]
