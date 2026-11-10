# EV-02: FQDN, DNS, dan HTTPS (Revisi 03 dan 03b)

| Item | Isi |
|---|---|
| Mahasiswa | Amelia Okta Ramadani (25832072004), kelas 2-A |
| Proyek | CloudLits (Sistem Cerdas Berbasis Cloud untuk Edukasi dan Peningkatan Kesadaran Literasi Digital) |
| Temuan dosen | 03: domain/FQDN belum definitif, alur DNS → HTTPS belum dibuktikan |
| Tanggal pengujian | 08-11-2026 (penerapan dan uji awal, dari laptop) dan 10-11-2026 (uji ulang setelah Stop/Start VM, dari Azure Cloud Shell) |
| FQDN yang diuji | `cloudlits-amelia.australiaeast.cloudapp.azure.com` |
| IPv4 publik | `20.58.180.44` |
| Status | **Lulus** secara teknis untuk FQDN Azure, termasuk setelah Stop/Start VM. Subdomain dari dosen belum diterima (lihat bagian 10). Keputusan akhir oleh dosen. |

Tidak ada password, private key, token, atau data siswa dalam berkas ini. Screenshot sudah diperiksa sebelum di-commit (centang setelah diperiksa): [ ]

## 1. Latar belakang dan keputusan

Dosen menyatakan subdomain akan dikirim setelah laporan memenuhi syarat. Karena HTTPS wajib dibuktikan lebih dulu, dipakai **DNS name label bawaan Azure** sebagai FQDN sementara yang sah. Dokumen arahan revisi membolehkan "alternatif yang sah" selama dependensi dan rencananya didokumentasikan.

Bila subdomain dosen diterima: tambahkan A record di zona domain dosen ke `20.58.180.44`, tambahkan nama itu pada Caddyfile, lalu ulangi uji bagian 5 sampai 8.

## 2. Identitas resource (Azure Portal)

| Properti | Nilai | Bukti |
|---|---|---|
| Public IP (resource) | `VpsAmel-ip` | `ev02/01-public-ip-overview.png` |
| Alamat | `20.58.180.44` | sama |
| SKU / Tier | Standard / Regional | sama |
| Assignment | Static | `ev02/02-public-ip-config.png` |
| DNS name label | `cloudlits-amelia` | sama |
| FQDN | `cloudlits-amelia.australiaeast.cloudapp.azure.com` | `ev02/01-public-ip-overview.png` |
| Terhubung ke | VM `VpsAmel` (NIC `vpsamel332`) | `ev02/01-public-ip-overview.png` |
| Status VM saat pemeriksaan awal | Stopped (deallocated), lalu dinyalakan (Running) | `ev02/03-vm-overview.png` |

Perubahan yang dilakukan: mengisi DNS name label pada Public IP. Tidak ada resource baru dan IP tidak berubah. Data yang sama diverifikasi ulang lewat Azure CLI pada 10-11-2026 (`ev01-vps-spec.md` bagian 2).

## 3. Uji DNS

### 3.1 Dari laptop, resolver publik Google 8.8.8.8 (08-11-2026)

`nslookup` dipakai karena `dig` tidak tersedia di Windows:

```text
nslookup cloudlits-amelia.australiaeast.cloudapp.azure.com 8.8.8.8
  Name:       cloudlits-amelia.australiaeast.cloudapp.azure.com
  Addresses:  64:ff9b::143a:b42c
              20.58.180.44

nslookup -type=AAAA cloudlits-amelia.australiaeast.cloudapp.azure.com 8.8.8.8
  Name:    cloudlits-amelia.australiaeast.cloudapp.azure.com
  Address: 64:ff9b::143a:b42c
```

Bukti: `ev02/04-nslookup.png`

### 3.2 Dari Azure Cloud Shell dengan `dig` (10-11-2026)

```text
$ dig +short cloudlits-amelia.australiaeast.cloudapp.azure.com A
20.58.180.44
```

| Pemeriksaan | Expected | Actual | Status |
|---|---|---|---|
| A record (8.8.8.8, 08-11) | `20.58.180.44` | `20.58.180.44` | Lulus |
| A record (`dig`, 10-11) | `20.58.180.44` | `20.58.180.44` | Lulus |
| IPv6 | Tidak ada IPv6 publik pada VM (portal: IPv6 kosong) | Jawaban AAAA `64:ff9b::143a:b42c` dari laptop | Dicatat |

Catatan IPv6: awalan `64:ff9b::/96` adalah awalan NAT64 yang memuat IPv4 `20.58.180.44` dalam heksadesimal (`143a:b42c`). Alamat ini sintetis dari jaringan laptop, bukan IPv6 milik VM. Penerbitan sertifikat tetap berhasil (bagian 5).

## 4. Firewall (dua lapis)

### 4.1 UFW di dalam VM

Sebelum perubahan: aktif, default `deny (incoming)`, aturan hanya 22/tcp dan 80/tcp (IPv4 dan IPv6).

Perintah: `sudo ufw allow 443/tcp` → `Rule added` dan `Rule added (v6)`.

Sesudah perubahan (`sudo ufw status verbose`): aturan `22/tcp`, `80/tcp`, `443/tcp` ALLOW IN Anywhere, beserta versi (v6). Diverifikasi ulang 10-11-2026 (`ev01-vps-spec.md` bagian 3.2).

Bukti: `ev02/05-ufw-sesudah.png`

### 4.2 NSG Azure (`VpsAmel-nsg`)

| Prioritas | Nama | Port | Protokol | Sumber | Aksi |
|---|---|---|---|---|---|
| 300 | SSH | 22 | TCP | `*` | Allow |
| 310 | Allow-HTTP-80 | 80 | TCP | `*` | Allow |
| 330 | Allow-HTTPS-443 | 443 | TCP | `*` | Allow (ditambah 08-11-2026) |

Bukti: `ev02/06-nsg.png`; diverifikasi ulang lewat `az network nsg list` pada 10-11-2026 (`ev01-vps-spec.md` bagian 2). Screenshot kondisi sebelum penambahan aturan 443 tidak diambil. Kondisi awal (hanya 22 dan 80) diambil dari laporan v0.2 dan inventaris M03.

## 5. Caddy dan sertifikat TLS

### 5.1 Konfigurasi

Caddyfile sebelum (`/etc/caddy/Caddyfile`, 41 byte):

```caddyfile
:80 {
    reverse_proxy 127.0.0.1:8000
}
```

Cadangan: `/etc/caddy/Caddyfile.bak-20261108` (ukuran sama, 41 byte).

Caddyfile sesudah:

```caddyfile
cloudlits-amelia.australiaeast.cloudapp.azure.com {
    reverse_proxy 127.0.0.1:8000
}
```

Validasi (`sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`): `Valid configuration`. Terdapat peringatan format (`caddy fmt`) yang tidak memengaruhi fungsi. Log validasi memuat `enabling automatic HTTP->HTTPS redirects`.

Penerapan: `sudo systemctl reload caddy`.

Bukti: `ev02/07-caddy-validate.png`

### 5.2 Penerbitan sertifikat (cuplikan log `journalctl -u caddy`)

Urutan kejadian pada log: `enabling automatic TLS certificate management` untuk FQDN, `new ACME account registered` (status valid), `trying to solve challenge` (http-01), beberapa `served key authentication`, `authorization finalized` (valid), dan **`certificate obtained successfully`** dengan penerbit `acme-v02.api.letsencrypt.org-directory`.

Pesan `no such file or directory` untuk berkas akun ACME adalah informasi bahwa akun belum ada, lalu akun baru dibuat. Itu bukan kegagalan.

Bukti: `ev02/08-caddy-log-sertifikat.png`

## 6. Uji dari luar server (laptop, Windows PowerShell, 08-11-2026)

Catatan: di PowerShell, `curl` adalah alias `Invoke-WebRequest`, sehingga dipakai `curl.exe`. Opsi `-k` tidak digunakan.

### 6.1 HTTPS

Perintah: `curl.exe -Iv https://cloudlits-amelia.australiaeast.cloudapp.azure.com/health`

Hasil penting: host di-resolve ke IPv4 `20.58.180.44`, koneksi ke port 443 terbentuk, respons `HTTP/1.1 200 OK`, `Server: gunicorn`, `Via: 1.1 Caddy`, `Date: Sun, 08 Nov 2026 09:03:39 GMT`.

Bukti: `ev02/09-curl-https.png`

### 6.2 Pengalihan HTTP ke HTTPS

Perintah: `curl.exe -I http://cloudlits-amelia.australiaeast.cloudapp.azure.com/health`

Hasil: `HTTP/1.1 308 Permanent Redirect`, `Location: https://cloudlits-amelia.australiaeast.cloudapp.azure.com/health`, `Server: Caddy`, `Date: Sun, 08 Nov 2026 09:04:23 GMT`.

Bukti: `ev02/10-curl-redirect.png`

## 7. Sertifikat (Microsoft Edge, Certificate Viewer, 08-11-2026)

| Properti | Nilai |
|---|---|
| Issued To (CN) | `cloudlits-amelia.australiaeast.cloudapp.azure.com` |
| Issued By | Let's Encrypt (CN `YE2`) |
| Berlaku dari | 8 November 2026 |
| Berlaku sampai | 6 Februari 2027 |
| Halaman `/health` | `{"status":"ok"}`, tanpa peringatan keamanan |

Bukti: `ev02/11-sertifikat-browser.png`. Waktu mulai berlaku sertifikat sekitar satu jam lebih awal daripada waktu penerbitan di log Caddy (Let's Encrypt memundurkan waktu mulai berlaku).

## 8. Uji ulang setelah Stop/Start VM (Azure Cloud Shell, 10-11-2026)

### 8.1 Kondisi

Pada 10-11-2026 VM dihentikan (`az vm deallocate`) dan dinyalakan kembali (`az vm start`) beberapa kali. Uji dilakukan setelah boot terakhir tanpa menjalankan perintah apa pun di VM untuk Caddy.

### 8.2 Perintah dan hasil

```bash
F=cloudlits-amelia.australiaeast.cloudapp.azure.com
date -u +%FT%TZ
az vm run-command invoke -g AmeliaOkta_ -n VpsAmel --command-id RunShellScript --scripts "uptime -s; systemctl is-enabled caddy; systemctl is-active caddy" --query "value[0].message" -o tsv
dig +short $F A
curl -sSI https://$F/health
curl -sS  https://$F/health
curl -sSI http://$F/health
curl -sSI --max-time 10 http://20.58.180.44/health
curl -sSI --max-time 10 https://20.58.180.44/health
echo | openssl s_client -connect $F:443 -servername $F 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

```text
== WAKTU UJI ==
2026-11-10T15:49:09Z
== BOOT VM & CADDY ==
2026-11-10 21:54:26
enabled
active
== DNS ==
20.58.180.44
== HTTPS ==
HTTP/2 200
date: Tue, 10 Nov 2026 15:49:44 GMT
server: gunicorn
via: 1.1 Caddy
== BODY ==
{"status":"ok"}
== HTTP -> HTTPS ==
HTTP/1.1 308 Permanent Redirect
Location: https://cloudlits-amelia.australiaeast.cloudapp.azure.com/health
Server: Caddy
== AKSES LEWAT IP (http) ==
HTTP/1.1 308 Permanent Redirect
Location: https://20.58.180.44/health
Server: Caddy
== AKSES LEWAT IP (https) ==
curl: (35) TLS connect error: error:0A000438:SSL routines::tlsv1 alert internal error
== SERTIFIKAT ==
subject=CN=cloudlits-amelia.australiaeast.cloudapp.azure.com
issuer=C=US, O=Let's Encrypt, CN=YE2
notBefore=Nov  8 08:03:10 2026 GMT
notAfter=Feb  6 08:03:09 2027 GMT
```

### 8.3 Penafsiran

- VM boot pukul 21:54:26 WIB; Caddy `enabled` sehingga otomatis aktif setelah boot, dan HTTPS langsung melayani `HTTP/2 200` tanpa campur tangan.
- Akses lewat IP dengan HTTP dialihkan Caddy ke `https://20.58.180.44/…`, tetapi koneksi TLS ke IP ditolak karena tidak ada sertifikat untuk alamat IP. Ini perilaku yang diharapkan: satu-satunya alamat resmi adalah FQDN.
- Sertifikat yang dilayani sama dengan sertifikat 08-11-2026 (CN sesuai FQDN, Let's Encrypt YE2, berlaku sampai 06-02-2027 08:03:09 GMT).

## 9. Ringkasan hasil uji

| ID | Pengujian | Expected | Actual | Status |
|---|---|---|---|---|
| T1 | DNS A record dari 8.8.8.8 | `20.58.180.44` | `20.58.180.44` | Lulus |
| T2 | Sertifikat TLS | Valid untuk FQDN | Let's Encrypt, CN sesuai FQDN, berlaku s.d. 06-02-2027 | Lulus |
| T3 | HTTPS `/health` dari luar | 200 tanpa `-k` | 200 OK | Lulus |
| T4 | HTTP ke HTTPS | 3xx dengan Location https | 308, Location https | Lulus |
| T5 | UFW dan NSG mengizinkan 443 | 443 diizinkan di kedua lapis | Diizinkan | Lulus |
| T6 | DNS dengan `dig` (10-11) | `20.58.180.44` | `20.58.180.44` | Lulus |
| T7 | HTTPS aktif setelah Stop/Start VM | 200 tanpa tindakan manual | `HTTP/2 200`, Caddy enabled/active | Lulus |
| T8 | Akses lewat IP | Bukan alamat resmi; tidak melayani HTTPS tanpa sertifikat valid | HTTP → 308; HTTPS via IP ditolak TLS | Lulus (sesuai desain) |
| T9 | Sertifikat setelah restart | Sama dan valid | CN FQDN, berlaku s.d. 06-02-2027 | Lulus |

## 10. Batasan dan isu tersisa

1. **Domain bukan final.** FQDN Azure adalah alternatif sementara. Subdomain dosen belum diterima.
2. **Perpanjangan sertifikat.** Sertifikat berlaku sampai 06-02-2027. Caddy memperpanjang otomatis menjelang habis masa berlaku, tetapi hanya bila VM menyala pada jendela perpanjangan (sekitar Januari 2027). Perpanjangan belum teramati; diperiksa ulang pada Januari 2027.
3. **SSH terbuka untuk `Any`.** NSG aturan SSH (prioritas 300) belum dibatasi. Gate "SSH tidak terekspos berlebihan" (M04) belum dinyatakan terpenuhi.
4. **HTTP/3.** Header `Alt-Svc: h3=":443"` muncul, tetapi UDP 443 tidak dibuka. Klien memakai HTTPS lewat TCP (HTTP/2).
5. **Screenshot NSG sebelum perubahan** tidak tersedia (lihat bagian 4.2).

Isu yang ditutup pada 10-11-2026: uji HTTPS setelah Stop/Start VM (T7) dan perilaku akses lewat IP lama (T8).

## 11. Daftar berkas bukti (folder `docs/evidence/ev02/`)

| Berkas | Isi |
|---|---|
| `01-public-ip-overview.png` | Overview Public IP: SKU Standard, FQDN, terhubung ke VM |
| `02-public-ip-config.png` | Configuration Public IP: Static, DNS name label |
| `03-vm-overview.png` | Overview VM (status Running, DNS name) |
| `04-nslookup.png` | `nslookup` A dan AAAA |
| `05-ufw-sesudah.png` | `ufw status verbose` dengan 443 |
| `06-nsg.png` | Inbound port rules NSG |
| `07-caddy-validate.png` | Caddyfile baru dan `caddy validate` |
| `08-caddy-log-sertifikat.png` | Log penerbitan sertifikat |
| `09-curl-https.png` | `curl.exe -Iv` HTTPS |
| `10-curl-redirect.png` | `curl.exe -I` HTTP (308) |
| `11-sertifikat-browser.png` | Certificate Viewer di browser |

Uji ulang 10-11-2026 (bagian 3.2 dan 8) disajikan sebagai teks keluaran Azure Cloud Shell.

## 12. Tautan ke dokumen laporan

Bagian laporan yang diperbarui: sorotan kuning (revisi 03, 08-11-2026) pada 1.1, 1.3, 1.4, 2.3, 6.2, 7.1, 7.2, 7.4, 8.3, 11.1, 11.3, 12 (M04), 13.2, 13.3, Lampiran C, dan 14.3; sorotan abu-abu muda (revisi 03b, 10-11-2026) pada 1.4, 11.1, 13.3, dan Lampiran C.
