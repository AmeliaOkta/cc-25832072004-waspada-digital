\# EV-02: FQDN, DNS, dan HTTPS (Revisi 03)



| Item | Isi |

|---|---|

| Mahasiswa | Amelia Okta Ramadani (25832072004), kelas 2-A |

| Proyek | CloudLits (Sistem Cerdas Berbasis Cloud untuk Edukasi dan Peningkatan Kesadaran Literasi Digital) |

| Temuan dosen | 03: domain/FQDN belum definitif, alur DNS → HTTPS belum dibuktikan |

| Tanggal pengujian | 08-11-2026 (WIB) |

| FQDN yang diuji | `cloudlits-amelia.australiaeast.cloudapp.azure.com` |

| IPv4 publik | `20.58.180.44` |

| Status | Lulus secara teknis untuk FQDN Azure. Subdomain dari dosen belum diterima (lihat bagian 9). Keputusan akhir oleh dosen. |



Tidak ada password, private key, token, atau data siswa dalam berkas ini. Screenshot sudah diperiksa sebelum di-commit (centang setelah diperiksa): \[ ]



\## 1. Latar belakang dan keputusan



Dosen menyatakan subdomain akan dikirim setelah laporan memenuhi syarat. Karena HTTPS wajib dibuktikan lebih dulu, dipakai \*\*DNS name label bawaan Azure\*\* sebagai FQDN sementara yang sah. Dokumen arahan revisi membolehkan "alternatif yang sah" selama dependensi dan rencananya didokumentasikan.



Bila subdomain dosen diterima: tambahkan A record di zona domain dosen ke `20.58.180.44`, tambahkan nama itu pada Caddyfile, lalu ulangi uji bagian 5 sampai 7.



\## 2. Identitas resource (Azure Portal)



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



Perubahan yang dilakukan: mengisi DNS name label pada Public IP. Tidak ada resource baru dan IP tidak berubah.



\## 3. Uji DNS (dari laptop, resolver publik Google 8.8.8.8)



Perintah dan hasil (`nslookup` dipakai karena `dig` tidak tersedia di Windows):



```

nslookup cloudlits-amelia.australiaeast.cloudapp.azure.com 8.8.8.8

&#x20; Name:       cloudlits-amelia.australiaeast.cloudapp.azure.com

&#x20; Addresses:  64:ff9b::143a:b42c

&#x20;             20.58.180.44



nslookup -type=AAAA cloudlits-amelia.australiaeast.cloudapp.azure.com 8.8.8.8

&#x20; Name:    cloudlits-amelia.australiaeast.cloudapp.azure.com

&#x20; Address: 64:ff9b::143a:b42c

```



Bukti: `ev02/04-nslookup.png`



| Pemeriksaan | Expected | Actual | Status |

|---|---|---|---|

| A record | `20.58.180.44` | `20.58.180.44` | Lulus |

| IPv6 | Tidak ada IPv6 publik pada VM (portal: IPv6 kosong) | Jawaban AAAA `64:ff9b::143a:b42c` | Dicatat |



Catatan IPv6: awalan `64:ff9b::/96` adalah awalan NAT64 yang memuat IPv4 `20.58.180.44` dalam heksadesimal (`143a:b42c`). Alamat ini diduga sintetis dan bukan IPv6 milik VM. Penerbitan sertifikat tetap berhasil (bagian 5).



\## 4. Firewall (dua lapis)



\### 4.1 UFW di dalam VM



Sebelum perubahan: aktif, default `deny (incoming)`, aturan hanya 22/tcp dan 80/tcp (IPv4 dan IPv6).



Perintah: `sudo ufw allow 443/tcp` → `Rule added` dan `Rule added (v6)`.



Sesudah perubahan (`sudo ufw status verbose`): aturan `22/tcp`, `80/tcp`, `443/tcp` ALLOW IN Anywhere, beserta versi (v6).



Bukti: `ev02/05-ufw-sesudah.png`



\### 4.2 NSG Azure (`VpsAmel-nsg`)



| Prioritas | Nama | Port | Protokol | Aksi |

|---|---|---|---|---|

| 300 | SSH | 22 | TCP | Allow |

| 310 | Allow-HTTP-80 | 80 | TCP | Allow |

| 330 | Allow-HTTPS-443 | 443 | TCP | Allow (ditambah 08-11-2026) |



Bukti: `ev02/06-nsg.png`. Screenshot kondisi sebelum penambahan aturan 443 tidak diambil. Kondisi awal (hanya 22 dan 80) diambil dari laporan v0.2 dan inventaris M03.



\## 5. Caddy dan sertifikat TLS



\### 5.1 Konfigurasi



Caddyfile sebelum (`/etc/caddy/Caddyfile`, 41 byte):



```

:80 {

&#x20;   reverse\_proxy 127.0.0.1:8000

}

```



Cadangan: `/etc/caddy/Caddyfile.bak-20261108` (ukuran sama, 41 byte).



Caddyfile sesudah:



```

cloudlits-amelia.australiaeast.cloudapp.azure.com {

&#x20;   reverse\_proxy 127.0.0.1:8000

}

```



Validasi (`sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`): `Valid configuration`. Terdapat peringatan format (`caddy fmt`) yang tidak memengaruhi fungsi. Log validasi memuat `enabling automatic HTTP->HTTPS redirects`.



Penerapan: `sudo systemctl reload caddy`.



Bukti: `ev02/07-caddy-validate.png`



\### 5.2 Penerbitan sertifikat (cuplikan log `journalctl -u caddy`)



Urutan kejadian pada log: `enabling automatic TLS certificate management` untuk FQDN, `new ACME account registered` (status valid), `trying to solve challenge` (http-01), beberapa `served key authentication`, `authorization finalized` (valid), dan \*\*`certificate obtained successfully`\*\* dengan penerbit `acme-v02.api.letsencrypt.org-directory`.



Pesan `no such file or directory` untuk berkas akun ACME adalah informasi bahwa akun belum ada, lalu akun baru dibuat. Itu bukan kegagalan.



Bukti: `ev02/08-caddy-log-sertifikat.png`



\## 6. Uji dari luar server (laptop, Windows PowerShell)



Catatan: di PowerShell, `curl` adalah alias `Invoke-WebRequest`, sehingga dipakai `curl.exe`. Opsi `-k` tidak digunakan.



\### 6.1 HTTPS



Perintah: `curl.exe -Iv https://cloudlits-amelia.australiaeast.cloudapp.azure.com/health`



Hasil penting: host di-resolve ke IPv4 `20.58.180.44`, koneksi ke port 443 terbentuk, respons `HTTP/1.1 200 OK`, `Server: gunicorn`, `Via: 1.1 Caddy`, `Date: Sun, 08 Nov 2026 09:03:39 GMT`.



Bukti: `ev02/09-curl-https.png`



\### 6.2 Pengalihan HTTP ke HTTPS



Perintah: `curl.exe -I http://cloudlits-amelia.australiaeast.cloudapp.azure.com/health`



Hasil: `HTTP/1.1 308 Permanent Redirect`, `Location: https://cloudlits-amelia.australiaeast.cloudapp.azure.com/health`, `Server: Caddy`, `Date: Sun, 08 Nov 2026 09:04:23 GMT`.



Bukti: `ev02/10-curl-redirect.png`



\## 7. Sertifikat (Microsoft Edge, Certificate Viewer)



| Properti | Nilai |

|---|---|

| Issued To (CN) | `cloudlits-amelia.australiaeast.cloudapp.azure.com` |

| Issued By | Let's Encrypt (CN `YE2`) |

| Berlaku dari | 8 November 2026 |

| Berlaku sampai | 6 Februari 2027 |

| Halaman `/health` | `{"status":"ok"}`, tanpa peringatan keamanan |



Bukti: `ev02/11-sertifikat-browser.png`. Waktu mulai berlaku sertifikat sekitar satu jam lebih awal daripada waktu penerbitan di log Caddy (Let's Encrypt memundurkan waktu mulai berlaku).



\## 8. Ringkasan hasil uji



| ID | Pengujian | Expected | Actual | Status |

|---|---|---|---|---|

| T1 | DNS A record dari 8.8.8.8 | `20.58.180.44` | `20.58.180.44` | Lulus |

| T2 | Sertifikat TLS | Valid untuk FQDN | Let's Encrypt, CN sesuai FQDN, berlaku s.d. 06-02-2027 | Lulus |

| T3 | HTTPS `/health` dari luar | 200 tanpa `-k` | 200 OK | Lulus |

| T4 | HTTP ke HTTPS | 3xx dengan Location https | 308, Location https | Lulus |

| T5 | UFW dan NSG mengizinkan 443 | 443 diizinkan di kedua lapis | Diizinkan | Lulus |



\## 9. Batasan dan isu tersisa



1\. \*\*Domain bukan final.\*\* FQDN Azure adalah alternatif sementara. Subdomain dosen belum diterima.

2\. \*\*Perpanjangan sertifikat.\*\* Sertifikat berlaku sampai 06-02-2027. Perpanjangan otomatis Caddy hanya dapat berjalan saat VM menyala. Perilaku ini belum diuji.

3\. \*\*SSH terbuka untuk `Any`.\*\* NSG aturan SSH (prioritas 300) belum dibatasi. Gate "SSH tidak terekspos berlebihan" (M04) belum dinyatakan terpenuhi.

4\. \*\*Belum diuji reboot.\*\* Caddy berstatus `enabled`, tetapi pengujian bahwa HTTPS kembali aktif setelah Stop/Start VM belum dilakukan pada berkas bukti ini.

5\. \*\*Akses via IP lama.\*\* `http://20.58.180.44/` tidak lagi menjadi alamat resmi. Perilaku persisnya belum diuji.

6\. \*\*HTTP/3.\*\* Header `Alt-Svc: h3=":443"` muncul, tetapi UDP 443 tidak dibuka. Klien memakai HTTPS lewat TCP.

7\. \*\*Screenshot NSG sebelum perubahan\*\* tidak tersedia (lihat bagian 4.2).



\## 10. Daftar berkas bukti (folder `docs/evidence/ev02/`)



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



\## 11. Tautan ke dokumen laporan



Bagian laporan yang diperbarui (ditandai sorotan kuning): 1.1, 1.3, 1.4, 2.3, 6.2, 7.1, 7.2, 7.4, 8.3, 11.1, 11.3, 12 (M04), 13.2, 13.3, Lampiran C, dan 14.3.

