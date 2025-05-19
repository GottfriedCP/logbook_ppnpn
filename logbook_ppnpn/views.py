from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from .forms import CatatanForm
from .models import Catatan

from models_master import ASN, PPNPN

from helper.utils import is_asn

JUMLAH_HARI_KERJA = 22


@login_required
def home(request):
    # redir ke laman validasi jika ASN
    if request.session.get("jenis_pegawai", False) == "asn":
        return redirect("logbook_ppnpn:list_validasi")

    nippnpn = request.session.get("ni", "-")
    ppnpn = PPNPN.objects.using("master").filter(nomor_induk=nippnpn).get()
    catatans = Catatan.objects.filter(nippnpn=nippnpn).order_by("-tanggal")
    context = {
        "page_title": "home",
        "ppnpn": ppnpn,
        "catatans": catatans,
    }
    return render(request, "logbook_ppnpn/home.html", context)


# @login_required
# def tampilkan_modal(request):
#     catatan_form = CatatanForm()
#     context = {
#         "catatan_form": catatan_form,
#     }
#     return render(request, "logbook_ppnpn/htmx/tambah_catatan_modal.html", context)


@login_required
def buat_catatan(request):
    """Buat dan simpan catatan baru utk sang PPNPN."""
    nippnpn = request.session.get("ni", "-")
    ppnpn = PPNPN.objects.using("master").filter(nomor_induk=nippnpn).get()
    form = CatatanForm()
    if request.method == "POST":
        form = CatatanForm(data=request.POST)
        if form.is_valid():
            catatan = form.save(commit=False)
            catatan.nippnpn = request.session.get("ni")
            catatan.save()
            messages.success(request, f"Entri berhasil dibuat")
        return redirect("logbook_ppnpn:home")

    context = {
        "page_title": "home",
        "form": form,
        "ppnpn": ppnpn,
    }
    return render(request, "logbook_ppnpn/tambah_catatan.html", context)


@login_required
def ubah_catatan(request, id_catatan):
    """Ubah dan simpan catatan baru utk sang PPNPN."""
    nippnpn = request.session.get("ni", "-")
    ppnpn = PPNPN.objects.using("master").filter(nomor_induk=nippnpn).get()
    catatan = get_object_or_404(Catatan, pk=id_catatan, nippnpn=ppnpn.nomor_induk)
    form = CatatanForm(instance=catatan)
    if request.method == "POST":
        form = CatatanForm(instance=catatan, data=request.POST)
        if form.is_valid():
            messages.success(request, f"Entri berhasil diubah")
            catatan = form.save()
        return redirect("logbook_ppnpn:home")

    context = {
        "page_title": "home",
        "ubah": True,
        "catatan_id": catatan.id,
        "form": form,
        "ppnpn": ppnpn,
    }
    return render(request, "logbook_ppnpn/tambah_catatan.html", context)


@login_required
def hapus_catatan(request, id_catatan):
    if request.method == "POST":
        cat = get_object_or_404(Catatan, pk=id_catatan)
        cat.delete()
        messages.success(request, f"Entri berhasil dihapus")
    return redirect("logbook_ppnpn:home")


@login_required
def cetak_logbook(request):
    if request.method == "POST":
        katim_id = request.POST.get("namaKatim")
        katim = get_object_or_404(ASN.objects.using("master"), id=katim_id)
        tanggal_dari = request.POST.get("dariTgl")
        tanggal_dari_parsed = datetime.strptime(tanggal_dari, "%m/%d/%Y")
        tanggal_dari_parsed = timezone.make_aware(tanggal_dari_parsed)
        tanggal_hingga = request.POST.get("hinggaTgl")
        tanggal_hingga_parsed = datetime.strptime(tanggal_hingga, "%m/%d/%Y")
        tanggal_hingga_parsed = timezone.make_aware(tanggal_hingga_parsed)
        nippnpn = request.session.get("ni", "-")
        ppnpn = PPNPN.objects.using("master").filter(nomor_induk=nippnpn).get()
        unit_kerja = request.POST.get("unitKerja")
        tim_kerja = request.POST.get("timKerja")

        catatans = Catatan.objects.filter(
            nippnpn=ppnpn.nomor_induk,
            tanggal__gte=tanggal_dari_parsed,
            tanggal__lte=tanggal_hingga_parsed,
        )
        context = {
            "katim": katim,
            "catatans": catatans,
            "ppnpn": ppnpn,
            "unit_kerja": unit_kerja,
            "tim_kerja": tim_kerja,
        }
        return render(request, "logbook_ppnpn/cetak_logbook.html", context)
    katims = ASN.objects.using("master").filter(level=1)
    context = {
        "page_title": "home",
        "katims": katims,
    }
    return render(request, "logbook_ppnpn/form_cetak_logbook.html", context)


def semua_logbook(request):
    """Laman nama-nama PPNPN untuk melihat logbook mereka."""
    ppnpns = PPNPN.objects.using("master").filter(aktif=True)
    # untuk PPNPN, tampilkan hanya dia saja di daftar
    if request.session.get("jenis_pegawai", False) == "ppnpn":
        ni_ppnpn = request.session.get("ni")
        ppnpns = ppnpns.filter(nomor_induk=ni_ppnpn)
    ppnpn_list = []
    for p in ppnpns:
        d = {}
        d["ni"] = p.nomor_induk
        d["nama"] = p.nama
        d["timker"] = p.nomor_timker
        # hitung capaian bulan ini
        bulan_ini = timezone.now().month
        catatans_count = (
            Catatan.objects.filter(nippnpn=p.nomor_induk, tanggal__month=bulan_ini)
            .annotate(tanggal_unik=TruncDate("tanggal"))
            .values("tanggal_unik")
            .distinct()
            .count()
        )
        capaian_sekarang = (
            Decimal(str(catatans_count))
            / Decimal(str(JUMLAH_HARI_KERJA))
            * Decimal("100.00")
        ).quantize(Decimal("00.00"), rounding=ROUND_HALF_UP)
        d["capaian_sekarang"] = capaian_sekarang
        # hitung capaian bulan sebelumnya
        bulan_lalu = (timezone.now().month - 2) % 12 + 1
        catatans_count = (
            Catatan.objects.filter(nippnpn=p.nomor_induk, tanggal__month=bulan_lalu)
            .annotate(tanggal_unik=TruncDate("tanggal"))
            .values("tanggal_unik")
            .distinct()
            .count()
        )
        capaian_lampau = (
            Decimal(str(catatans_count))
            / Decimal(str(JUMLAH_HARI_KERJA))
            * Decimal("100.00")
        ).quantize(Decimal("00.00"), rounding=ROUND_HALF_UP)
        d["capaian_lampau"] = capaian_lampau
        ppnpn_list.append(d)
    context = {
        "page_title": "semua_logbook",
        "ppnpns": ppnpn_list,
    }
    return render(request, "logbook_ppnpn/semua_logbook.html", context)


def detail_logbook(request, id_ppnpn):
    ppnpn = PPNPN.objects.using("master").filter(nomor_induk=id_ppnpn).get()
    catatans = Catatan.objects.filter(nippnpn=id_ppnpn).order_by("-tanggal")
    context = {
        "page_title": "semua_logbook",
        "ppnpn": ppnpn,
        "catatans": catatans,
    }
    return render(request, "logbook_ppnpn/detail_logbook.html", context)


@login_required
def list_validasi(request):
    nip = request.session.get("ni")
    asn = ASN.objects.using("master").get(nip=nip)
    timker = asn.nomor_timker
    # query semua NI ppnpn di timker ini
    nippnpns = (
        PPNPN.objects.using("master")
        .filter(nomor_timker=timker)
        .values_list("nomor_induk", flat=True)
    )
    catatans = Catatan.objects.filter(verified=False, nippnpn__in=list(nippnpns))
    catatans = catatans.order_by("-tanggal").values()
    catatans = list(catatans)
    for c in catatans:
        c["nama_ppnpn"] = (
            PPNPN.objects.using("master").get(nomor_induk=c["nippnpn"]).nama
        )

    context = {
        "page_title": "home",
        "catatans": catatans,
    }
    return render(request, "logbook_ppnpn/list_validasi.html", context)


@login_required
def validasi(request, id_catatan):
    if request.method == "POST":
        catatan = get_object_or_404(Catatan, id=id_catatan)
        ppnpn = PPNPN.objects.using("master").get(nomor_induk=catatan.nippnpn)
        # validasi catatan
        catatan.verified = True
        catatan.verified_at = timezone.now()
        catatan.save()
        messages.success(request, f"Entri {ppnpn.nama} berhasil divalidasi")
    return redirect("logbook_ppnpn:list_validasi")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("logbook_ppnpn:home")

    if request.method == "POST":
        nip = request.POST.get("nip")
        password = request.POST.get("password")
        password_ok = nip == password
        if is_asn(nip):
            ni_exists = ASN.objects.using("master").filter(nip=nip).exists()
        else:
            ni_exists = PPNPN.objects.using("master").filter(nomor_induk=nip).exists()

        if password_ok and ni_exists:
            user = authenticate(request, username="user", password="user")

            if user is not None:
                login(request, user)
                if is_asn(nip):
                    asn = ASN.objects.using("master").filter(nip=nip).get()
                    # REQUEST SESSION
                    request.session["ni"] = asn.nip
                    request.session["jenis_pegawai"] = "asn"
                    return redirect("logbook_ppnpn:list_validasi")
                else:
                    ppnpn = PPNPN.objects.using("master").filter(nomor_induk=nip).get()
                    # REQUEST SESSION
                    request.session["ni"] = ppnpn.nomor_induk
                    request.session["jenis_pegawai"] = "ppnpn"
                    return redirect("logbook_ppnpn:home")
            else:
                messages.error(request, "Base user belum ada.")
        messages.error(request, "NIP atau kata sandi salah.")
    return render(
        request,
        "login.html",
        {
            "hide_navbar": True,
        },
    )


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("logbook_ppnpn:home")
