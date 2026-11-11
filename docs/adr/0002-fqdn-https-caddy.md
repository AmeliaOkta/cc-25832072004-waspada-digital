# ADR-0002: FQDN Azure, HTTPS dengan Caddy, dan firewall dua lapis

| Item | Isi |
|---|---|
| Status | Accepted (08-11-2026) |
| Tanggal | 08-11-2026; ditinjau 10-11-2026 |
| Penulis | Amelia Okta Ramadani (25832072004) |
| Terkait | Temuan audit 03; `docs/evidence/ev02-https.md`; ADR-0001 |

## Konteks

- Aplikasi CloudLits berjalan di satu VM Azure `Standard_B2ats_v2` (Australia East), Gunicorn di `127.0.0.1:8000`, Caddy sebagai reverse proxy.
- Sampai 08-11-2026 aplikasi hanya dapat diakses lewat `http://20.58.180.44` tanpa TLS.
- Dosen akan memberikan subdomain setelah laporan memenuhi syarat, tetapi HTTPS wajib dibuktikan lebih dulu (Temuan 03).
- Arahan revisi membolehkan "alternatif yang sah" bila domain belum tersedia, selama dependensi dan rencananya didokumentasikan.

## Keputusan

1. Memakai **DNS name label Azure** pada public IP `VpsAmel-ip` sebagai FQDN sementara: `cloudlits-amelia.australiaeast.cloudapp.azure.com` (IP Static `20.58.180.44`).
2. **Caddy** melayani FQDN tersebut dengan sertifikat **Let's Encrypt** otomatis (tantangan HTTP-01) dan pengalihan otomatis HTTP → HTTPS (308).
3. **TCP/443** dibuka di dua lapis: NSG Azure (prioritas 330) dan UFW di VM; port 80 tetap terbuka untuk tantangan ACME dan pengalihan.
4. Akses lewat alamat IP bukan lagi alamat resmi.

## Alternatif yang dipertimbangkan

| Alternatif | Alasan tidak dipilih |
|---|---|
| Menunggu subdomain dosen | HTTPS harus dibuktikan sebelum subdomain diberikan |
| Membeli domain sendiri | Menambah biaya kas; tidak diperlukan untuk praktikum |
| Sertifikat self-signed | Tidak dipercaya browser; tidak memenuhi kriteria "sertifikat TLS valid" |
| NGINX + Certbot | Konfigurasi dan perpanjangan lebih banyak langkah; Caddy sudah dipakai sejak M03 |

## Konsekuensi

- Positif: HTTPS valid tanpa biaya, perpanjangan sertifikat otomatis, konfigurasi Caddyfile tiga baris; terbukti aktif kembali setelah Stop/Start VM (ev02, 10-11-2026).
- Negatif: FQDN panjang dan terikat pada Azure; bila IP atau label dihapus, FQDN hilang.
- Perpanjangan sertifikat hanya berjalan bila VM menyala pada jendela perpanjangan (sekitar Januari 2027; sertifikat berlaku s.d. 06-02-2027).
- Aturan SSH di NSG masih bersumber `*`; pembatasan ditangani terpisah (gate M04).

## Rencana bila subdomain dosen diterima

1. Tambahkan A record subdomain ke `20.58.180.44` di zona DNS dosen.
2. Tambahkan nama subdomain ke Caddyfile (boleh bersama FQDN Azure), `caddy validate`, lalu `systemctl reload caddy`.
3. Ulangi uji `dig`, `curl -Iv https://…`, redirect, dan pemeriksaan sertifikat; catat di ev02.

## Bukti

`docs/evidence/ev02-https.md` (uji 08-11-2026 dan uji ulang 10-11-2026).
