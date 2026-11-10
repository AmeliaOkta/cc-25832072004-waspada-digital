# EV-06: Restore Database SQLite dari Azure Blob (Revisi 02 dan 02b)

| Item | Isi |
|---|---|
| Mahasiswa | Amelia Okta Ramadani (25832072004), kelas 2-A |
| Proyek | CloudLits |
| Temuan dosen | 02 (P0): belum ada bukti pelaksanaan restore yang dapat dinilai |
| Tanggal pengujian | 09-11-2026 (metode A dan B, di VM) dan 10-11-2026 (metode D, lingkungan terpisah). Waktu pada log dalam UTC; WIB = UTC+7 |
| Lingkungan | Metode A/B: VM `VpsAmel` (host `cc-m03-25832072004`), Ubuntu 24.04.5, SQLite CLI 3.45.1. Metode D: Azure Cloud Shell (`SandboxHost-639299107127875151`), Python sqlite3 3.44.0 |
| Sumber restore | Azure Blob privat `cloudlitsbackupamel/sqlite-backups`, awalan `harian/` |
| Backup yang dipulihkan | A/B: `cloudlits-20261109T101910Z.db` (17:19:10 WIB). D: `cloudlits-20261110T140550Z.db` (21:05:50 WIB, dibuat oleh timer) |
| Status | **Lulus** untuk pemulihan database (data sintetis), termasuk restore ke lingkungan terpisah saat VM tidak tersedia. **Sebagian** untuk RTO penuh (rebuild VM dan aplikasi belum diuji). Batasan pada bagian 9. Keputusan akhir oleh dosen. |

Tidak ada password, token, atau data siswa dalam berkas ini. Database berisi data sintetis (30 pengguna dan 90 percobaan kuis). Screenshot sudah diperiksa sebelum di-commit (centang): [ ]

## 1. Cakupan dan metode

Aplikasi Flask belum memakai SQLite (laporan: integrasi tidak dicakup revisi 01). Karena itu uji ini membuktikan **pemulihan database**, bukan pemulihan aplikasi utuh.

| Metode | Dilakukan | Alasan |
|---|---|---|
| A. Restore ke folder uji terpisah di VM | Ya (09-11-2026) | Aman, tidak menyentuh data asli |
| B. Simulasi kehilangan data pada VM yang sama (database diganti nama, lalu dipulihkan dari Azure) | Ya (09-11-2026) | Pemulihan nyata dengan waktu terukur, berkas asli tetap aman |
| C. Restore ke VM kedua / rebuild VM | Tidak | Biaya tambahan dari kredit Azure for Students; dicatat sebagai batasan |
| **D. Restore ke lingkungan terpisah (Azure Cloud Shell) saat VM dalam keadaan deallocated** | **Ya (10-11-2026)** | Memenuhi kriteria dosen bagian VI ("restore ke lingkungan terpisah teruji") tanpa resource tambahan |

Metode A dan B memakai Managed Identity VM, sama seperti skrip backup. Metode D memakai Azure CLI di Cloud Shell dengan akun pemilik langganan; tidak ada secret yang dicetak atau disimpan.

## 2. Kondisi awal (09-11-2026)

Isi `~/cloudlits-data` sebelum uji: `backup-sqlite.sh` (2.051 byte), `backup.log`, `cloudlits.db` (24.576 byte, izin 600), `skema.sql`, folder `staging`, dan folder `verifikasi`.

Salinan lokal di `staging`: tiga himpunan (`094851Z` tanpa manifest, `095706Z` dan `101910Z` lengkap).

Daftar blob dari Azure (perintah memakai token Managed Identity; token tidak dicetak):

```
harian/cloudlits-20261109T094851Z.db
harian/cloudlits-20261109T094851Z.db.sha256
harian/cloudlits-20261109T095706Z.db
harian/cloudlits-20261109T095706Z.db.manifest.json
harian/cloudlits-20261109T095706Z.db.sha256
harian/cloudlits-20261109T101910Z.db
harian/cloudlits-20261109T101910Z.db.manifest.json
harian/cloudlits-20261109T101910Z.db.sha256
```

Manifest backup yang dipakai: ukuran 24.576 byte, `integrity_check` ok, baris `pengguna` 30 dan `percobaan_kuis` 90, SHA-256 `dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044`, metode `sqlite3 .backup (Online Backup API)`.

Bukti: `ev06/01-kondisi-awal.png`, `ev06/02-daftar-blob.png`

## 3. Metode A: unduh dari Azure ke folder uji

Folder `~/cloudlits-data/restore-uji` (izin 700). Hasil: tiga berkas `HTTP 200`, ukuran `.db` 24.576 byte, `.sha256` 96 byte, `.manifest.json` 348 byte. Waktu: mulai dan selesai sama pada resolusi satu detik (10:40:56Z).

Bukti: `ev06/03-unduh-folder-uji.png`

### 3.1 Verifikasi hasil unduhan

| Pemeriksaan | Hasil |
|---|---|
| `sha256sum -c` | `cloudlits-20261109T101910Z.db: OK` |
| SHA-256 di manifest | `dcbd8933...008044` (sama dengan nilai di `backup.log`) |
| `PRAGMA integrity_check` (`-readonly`) | `ok` |
| Row count | `pengguna` 30, `percobaan_kuis` 90 (sama dengan manifest) |

Bukti: `ev06/04-verifikasi-folder-uji.png`

## 4. Metode B: baseline, simulasi kehilangan, dan restore di VM

### 4.1 Baseline database asli (sebelum simulasi)

| Pemeriksaan | Hasil |
|---|---|
| `integrity_check` | ok |
| Row count | 30 dan 90 |
| SHA-256 berkas | `265f4a5b9ef71a59e9b95b0e1a35e85a1884ef91af5bc210267d1d4f4694d747` |
| Hash logis cara 1 (`sqlite3 .dump` lalu SHA-256) | `304a9abb46408200094cbcfca1177401fdf4b90be9a75da8787d77e212f588e1` |
| Hash logis cara 1 hasil restore folder uji | `304a9abb...88e1` (identik dengan database asli) |

Hash berkas asli berbeda dengan hash berkas backup, dan itu diharapkan: `sqlite3 .backup` menyalin isi logis, bukan susunan byte. Kesetaraan dibuktikan dengan hash logis.

Bukti: `ev06/05-baseline-asli.png`

### 4.2 Pemeriksaan ketergantungan aplikasi

`grep` pada berkas `.py`, `.service`, `.env` di folder rumah: tidak ada yang menyebut `cloudlits.db`. `fuser`: tidak ada proses yang membukanya (kode keluar 1). Pemeriksaan ini terbatas pada folder rumah dan kondisi saat itu. File layanan di `/etc/systemd/system/` tidak diperiksa.

### 4.3 Simulasi kehilangan data (T0)

```
T0 (data hilang)   2026-11-09T10:43:40Z  (17:43:40 WIB)
health sebelum: HTTP 200
mv cloudlits.db cloudlits.db.hilang-sim
ls: cannot access 'cloudlits.db': No such file or directory
Error: unable to open database "cloudlits.db": unable to open database file
health sesudah: HTTP 200
```

Berkas asli tidak dihapus: dipertahankan sebagai `cloudlits.db.hilang-sim` (24.576 byte, izin 600).

Bukti: `ev06/06-simulasi-kehilangan.png`

### 4.4 Prosedur restore (`restore-sqlite.sh`, 1.822 byte, tanpa secret)

Tahapan skrip: menolak jalan bila `cloudlits.db` sudah ada (tidak menimpa), mengunduh tiga berkas ke folder sementara `pulih-tmp`, memeriksa checksum, `integrity_check`, dan row count, baru memindahkan berkas menjadi database aktif dan mengatur izin 600. Setiap tahap gagal akan menghentikan skrip. Sintaks diperiksa dengan `bash -n` (OK). Berkas skrip: `docs/evidence/ev06/restore-sqlite.sh`.

Pemeriksaan ulang 10-11-2026 (lewat `az vm run-command invoke`):

```text
grep -n -i -E 'accountkey|account_key|sas|sig=|password|connectionstring' restore-sqlite.sh
tidak ada pola secret
```

### 4.5 Pelaksanaan restore

```
T1 (mulai restore)   2026-11-09T10:45:37Z
2026-11-09T10:45:37Z MULAI restore cloudlits-20261109T101910Z.db
2026-11-09T10:45:37Z UNDUH cloudlits-20261109T101910Z.db HTTP 200
2026-11-09T10:45:37Z UNDUH cloudlits-20261109T101910Z.db.sha256 HTTP 200
2026-11-09T10:45:37Z UNDUH cloudlits-20261109T101910Z.db.manifest.json HTTP 200
2026-11-09T10:45:38Z CHECKSUM OK
2026-11-09T10:45:38Z INTEGRITY ok
2026-11-09T10:45:38Z ROW pengguna=30 percobaan_kuis=90
2026-11-09T10:45:38Z SELESAI restore ke /home/azureuseramel/cloudlits-data/cloudlits.db durasi=1 detik
real    0m0.235s
T2 (selesai restore)  2026-11-09T10:45:38Z
-rw------- 1 azureuseramel azureuseramel 24576 Nov  9 17:45 cloudlits.db
```

Isi `restore.log` di atas diambil ulang dari VM pada 10-11-2026 dan identik dengan tangkapan 09-11-2026.

Bukti: `ev06/07-restore-log.png`

### 4.6 Verifikasi akhir (dipulihkan dibanding yang hilang)

| Pemeriksaan | Hasil |
|---|---|
| `integrity_check` | ok |
| Row count | 30 dan 90 |
| Hash logis cara 1 database dipulihkan | `304a9abb46408200094cbcfca1177401fdf4b90be9a75da8787d77e212f588e1` |
| Hash logis cara 1 `cloudlits.db.hilang-sim` | `304a9abb46408200094cbcfca1177401fdf4b90be9a75da8787d77e212f588e1` |
| Folder sementara `pulih-tmp` | tidak ada (dibersihkan skrip) |
| `/health` | HTTP 200 |

Bukti: `ev06/08-verifikasi-akhir.png`

## 5. Metode D: restore ke lingkungan terpisah saat VM tidak tersedia (10-11-2026)

### 5.1 Kondisi

- VM `VpsAmel` dalam status **Stopped (deallocated)** (`az vm deallocate -g AmeliaOkta_ -n VpsAmel` dijalankan sebelum T0). Ini menyimulasikan VM yang tidak dapat diakses.
- Restore dilakukan di Azure Cloud Shell, mesin yang berbeda dari VM, tanpa SSH dan tanpa key VM.
- Backup yang dipakai adalah backup terbaru, dibuat otomatis oleh `cloudlits-backup.timer` (lihat ev05).
- Database dibuka dalam mode baca-saja (`mode=ro`) sehingga verifikasi tidak mengubah berkas.

### 5.2 Perintah

```bash
mkdir -p ~/ev06 && cd ~/ev06
B=cloudlits-20261110T140550Z.db
T0=$(date -u +%FT%TZ)
for f in $B $B.sha256 $B.manifest.json; do
  az storage blob download --account-name cloudlitsbackupamel -c sqlite-backups --auth-mode key -n "harian/$f" -f "$f" --only-show-errors -o none
done
T1=$(date -u +%FT%TZ)
sha256sum -c $B.sha256
python3 - "$B" <<'PY'
import sqlite3, hashlib, sys
c = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
print("sqlite_version   :", sqlite3.sqlite_version)
print("integrity_check  :", c.execute("PRAGMA integrity_check").fetchone()[0])
for t in [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]:
    print(f"baris {t:<15}:", c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0])
print("hash_logis       :", hashlib.sha256("\n".join(c.iterdump()).encode()).hexdigest())
PY
T2=$(date -u +%FT%TZ)
hostname; uname -sr
```

### 5.3 Output

```text
T0 mulai restore      : 2026-11-10T14:50:26Z
T1 unduhan selesai    : 2026-11-10T14:50:36Z
== cek checksum ==
cloudlits-20261110T140550Z.db: OK
== cek database ==
sqlite_version   : 3.44.0
integrity_check  : ok
baris pengguna       : 30
baris percobaan_kuis : 90
hash_logis       : 95836d334cf071f87a82a9bf1137d9837ca22668a8924b47a898ca44d1568be1
T2 verifikasi selesai : 2026-11-10T14:50:38Z
== lingkungan ==
SandboxHost-639299107127875151
Linux 6.1.158.2-microsoft-standard
```

### 5.4 Pembanding: database aktif di VM

Setelah VM dinyalakan kembali (`az vm start`), hash logis database aktif `cloudlits.db` dihitung dengan cara yang sama (Python `iterdump`, mode baca-saja, lewat `az vm run-command invoke`):

```text
== HASH LOGIS DB ASLI DI VM ==
95836d33 4cf071f8 7a82a9bf 1137d983 7ca22668 a8924b47 a898ca44 d1568be1
integrity: ok
```

| Sumber | Hash logis cara 2 (Python `iterdump` lalu SHA-256) | Cocok |
|---|---|---|
| Database aktif di VM (`cloudlits.db`) | `95836d334cf071f87a82a9bf1137d9837ca22668a8924b47a898ca44d1568be1` | — |
| Hasil restore metode D di Cloud Shell | `95836d334cf071f87a82a9bf1137d9837ca22668a8924b47a898ca44d1568be1` | **YA** |

### 5.5 Catatan dua cara hash logis

Uji 09-11-2026 memakai **cara 1** (`sqlite3 .dump` di VM), sedangkan uji 10-11-2026 memakai **cara 2** (Python `iterdump`) karena Cloud Shell tidak menyediakan CLI `sqlite3`. Teks dump kedua cara tidak sama persis (format dan urutan pernyataan berbeda), sehingga nilai hash-nya berbeda (`304a9abb…` dan `95836d33…`) walaupun datanya sama. Kesetaraan selalu dibandingkan dengan **cara yang sama**: cara 1 identik pada metode A/B, cara 2 identik pada metode D. Hash berkas `.db` di Blob (`dcbd8933…`) sama pada kedua backup, karena database tidak berubah antara 09-11 dan 10-11-2026.

### 5.6 Waktu

| Titik | Waktu (UTC) | Selisih dari T0 |
|---|---|---|
| T0 — mulai restore | 14:50:26 | 0 detik |
| T1 — tiga berkas selesai diunduh dari Blob | 14:50:36 | 10 detik |
| T2 — checksum, integritas, baris, hash logis selesai | 14:50:38 | **12 detik** |

## 6. Pengukuran RPO dan RTO

| Ukuran | Hasil | Target di laporan |
|---|---|---|
| Durasi prosedur restore (metode B) | 1 detik pada log (`real` 0,235 detik) | |
| T0 sampai T2 (metode B, VM yang sama) | 1 menit 58 detik (10:43:40Z sampai 10:45:38Z), termasuk jeda antar-perintah oleh operator | RTO: maksimum 60 menit |
| T0 sampai T2 (metode D, lingkungan terpisah) | 12 detik (14:50:26Z sampai 14:50:38Z) | RTO: maksimum 60 menit |
| Umur backup saat data "hilang" (metode B) | 24 menit 30 detik (10:19:10Z sampai 10:43:40Z) | RPO: maksimum 24 jam |
| Data yang hilang secara aktual | Tidak ada (hash logis sama) | |
| RTO penuh (VM baru + deploy aplikasi + restore) | **Belum diukur** | RTO: maksimum 60 menit |

Penafsiran yang jujur: angka RTO hanya mencakup pemulihan database, dengan data kecil dan sintetis. Angka itu tidak mencakup deteksi kejadian, pembangunan ulang VM, deploy aplikasi, atau keputusan manusia. Data yang hilang nol karena tidak ada penulisan baru antara backup dan simulasi, bukan karena jaminan sistem. Bila VM mati pada jam jadwal 02:00 WIB, backup disusulkan saat VM menyala (ev05), sehingga RPO efektif = selang sejak VM terakhir menyala. Resolusi log satu detik.

## 7. Hasil uji

| ID | Pengujian | Expected | Actual | Status |
|---|---|---|---|---|
| R1 | Backup ditemukan di Azure lewat API | Ada di luar VM | 8 blob di `harian/` (09-11); 11 blob (10-11) | Lulus |
| R2 | Unduh dari Azure | HTTP 200, ukuran sama manifest | 200, 24.576 byte | Lulus |
| R3 | Checksum | OK | `sha256sum -c` OK | Lulus |
| R4 | `integrity_check` hasil restore | ok | ok | Lulus |
| R5 | Row count | 30 dan 90 | 30 dan 90 | Lulus |
| R6 | Hash logis hasil restore vs asli (cara 1) | Identik | Identik | Lulus |
| R7 | Simulasi kehilangan data | Database tidak dapat dibuka | `unable to open database file` | Lulus |
| R8 | Pemulihan ke lokasi semula | Database kembali dengan izin 600 | Kembali, 24.576 byte, izin 600 | Lulus |
| R9 | Hasil restore vs data yang hilang (cara 1) | Hash logis identik | Identik | Lulus |
| R10 | RTO (database, VM yang sama) | maksimum 60 menit | 1 menit 58 detik | Lulus untuk cakupan database |
| R11 | RPO | maksimum 24 jam | jendela 24 menit 30 detik | Lulus untuk skenario uji |
| R12 | Restore ke lingkungan terpisah saat VM tidak tersedia | Berhasil tanpa login ke VM | Cloud Shell, VM deallocated | Lulus |
| R13 | Checksum dan integritas di lingkungan terpisah | OK dan ok | OK dan ok | Lulus |
| R14 | Hash logis hasil restore D vs database aktif VM (cara 2) | Identik | Identik | Lulus |
| R15 | RTO (database, lingkungan terpisah) | maksimum 60 menit | 12 detik | Lulus untuk cakupan database |
| R16 | RTO penuh (rebuild VM + aplikasi) | maksimum 60 menit | Belum diuji | Belum |

## 8. Isu revisi sebelumnya yang sudah ditutup (10-11-2026)

| Isu di draf 09-11-2026 | Status 10-11-2026 | Bukti |
|---|---|---|
| Restore hanya di VM yang sama | Ditutup sebagian: restore ke lingkungan terpisah terbukti (metode D); rebuild VM tetap belum | Bagian 5 |
| Timer 02:00 WIB belum terbukti terpicu sendiri | Ditutup | ev05 bagian 5.1 (`LastTriggerUSec` 21:05:50 WIB) |
| Retensi 14 hari belum diterapkan di Azure | Ditutup | ev05 bagian 4 (lifecycle rule `hapus-backup-14-hari`) |
| Pembatasan jaringan Storage | Diputuskan tetap `Allow` dengan mitigasi | ev05 bagian 9 |

## 9. Batasan dan isu tersisa

1. **RTO penuh belum diuji.** Pembangunan VM baru dari repository, deploy aplikasi, dan restore ke VM tersebut (metode C) belum dilakukan karena biaya; dijadwalkan M12.
2. **Aplikasi belum memakai SQLite.** Pemulihan aplikasi utuh belum terbukti. Pembuktian lanjutan pada M05 dan M12.
3. **Data kecil dan sintetis.** Durasi pada data riil dapat lebih lama.
4. **Backup dipilih manual.** Skrip menerima nama berkas backup sebagai argumen. Pemilihan otomatis backup terbaru belum dibuat.
5. **Checksum dan manifest satu tempat dengan `.db`.** Checksum mendeteksi kerusakan atau unduhan tidak utuh, tetapi tidak melindungi bila semua berkas diubah sekaligus. `backup.log` di VM menjadi pembanding independen kecil.
6. **Hash berkas setelah dipindah** tidak diukur ulang. Kesetaraan dibuktikan dengan hash logis.
7. **Dua cara hash logis** (bagian 5.5): perbandingan hanya sah dalam cara yang sama.
8. **Pemeriksaan ketergantungan aplikasi terbatas** pada folder rumah dan kondisi saat itu (bagian 4.2).
9. **Salinan sementara menumpuk di `staging`** (128 KB per 10-11-2026); pembersihan otomatis belum ada.
10. **Izin berkas di `restore-uji/` adalah 664**, lebih longgar dari database utama (600). Risiko rendah karena folder induk 700.
11. **Sisa uji dipertahankan sampai penilaian selesai:** folder `restore-uji` dan berkas `cloudlits.db.hilang-sim`.

## 10. Daftar berkas bukti (folder `docs/evidence/ev06/`)

| Berkas | Isi |
|---|---|
| `01-kondisi-awal.png` | Isi `cloudlits-data` dan `staging` |
| `02-daftar-blob.png` | Daftar 8 blob dari Azure |
| `03-unduh-folder-uji.png` | Unduhan ke `restore-uji` (HTTP 200, ukuran) |
| `04-verifikasi-folder-uji.png` | Checksum, integrity, row count |
| `05-baseline-asli.png` | Baseline database asli dan hash logis |
| `06-simulasi-kehilangan.png` | T0, `mv`, galat pembukaan, `health` |
| `07-restore-log.png` | T1, log restore, T2 |
| `08-verifikasi-akhir.png` | Perbandingan akhir dan `health` |
| `restore-sqlite.sh` | Skrip restore (tanpa secret) |

Bukti metode D dan pembanding hash VM disalin sebagai teks pada bagian 5 (keluaran Azure Cloud Shell, 10-11-2026).

## 11. Tautan ke laporan

Bagian laporan yang diperbarui: sorotan oranye (revisi 02, 09-11-2026) dan abu-abu muda (revisi 02b, 10-11-2026); lihat catatan revisi pada bagian 1.4. Hash commit berkas ini dicantumkan di laporan (tabel status temuan baris 02 dan evidence register EV-04).
