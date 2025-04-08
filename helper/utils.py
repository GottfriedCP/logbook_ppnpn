def is_asn(ni: str) -> bool:
    """Cek apakah pegawai termasuk ASN atau PPNPN"""
    # ni = nomor induk
    return str(ni).startswith("19")
