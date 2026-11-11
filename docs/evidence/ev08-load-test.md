# EV-08: Uji Beban (Load Test) Aplikasi CloudLits M03

| Item | Isi |
|---|---|
| Proyek | CloudLits — CC-PTI2802-25832072004-CLOUDLITS |
| Mahasiswa | Amelia Okta Ramadani (25832072004) |
| Acuan arahan | Bagian IV.4 (performa) dan VI ("pengujian fungsi inti, akses peran, dan beban memiliki hasil nyata"); paket penyerahan `ev08-load-test.md` |
| Kebutuhan laporan | NFR-04 (performa) dan NFR-05 (kapasitas) |
| Tanggal uji | 11-11-2026, 11:34–11:38 WIB |
| Versi aplikasi | Aplikasi M03 (Flask + Gunicorn 1 worker/2 thread + Caddy), konten dari `cases.json` (4 studi kasus); route `/`, `/api/info`, `/health` |
| Status | **LULUS** untuk skenario 5 pengguna bersamaan pada aplikasi M03. Halaman kuis belum ada; uji diulang pada M11 |

> Tidak ada data siswa, secret, atau Subscription ID dalam berkas ini.

## 1. Batas lulus (ditetapkan di laporan sebelum pengukuran)

| Kode | Kriteria | Batas |
|---|---|---|
| NFR-04 | Latensi p95 halaman materi pada 5 pengguna bersamaan, diukur dari jaringan di Indonesia | ≤ 2.000 ms |
| 9.2 | Error rate respons 5xx terhadap request valid | < 1% |
| NFR-05 | RAM puncak | ≤ 80% RAM tersedia |
| NFR-05 | Pemakaian disk | ≤ 50% |

## 2. Skenario dan alat

| Aspek | Nilai |
|---|---|
| Alat | Skrip Python `loadtest.py` (pustaka standar, tanpa dependensi), terlampir di `ev08/loadtest.py` |
| Klien | Laptop Windows, Python 3.13.15, di Indonesia, tersambung lewat **hotspot ponsel** |
| Target | `https://cloudlits-amelia.australiaeast.cloudapp.azure.com` (Australia East); sertifikat TLS diverifikasi |
| Beban | 5 pengguna bersamaan (5 thread), tiap pengguna mengirim permintaan berturut-turut tanpa jeda |
| Komposisi | 50% `/` (halaman materi), 25% `/api/info`, 25% `/health` |
| Durasi | 60 detik pengukuran + 5 detik pemanasan (tidak dihitung) |
| Pengulangan | 2 kali |
| Koneksi | Koneksi baru untuk setiap permintaan (termasuk jabat tangan TLS), sehingga latensi mencerminkan kondisi terburuk tanpa *keep-alive* |
| Pemantauan server | `vmstat -S M 5`, `free -m`, `ps` (RSS Gunicorn), `df -h /`; dijalankan di VM lewat `az vm run-command` |

## 3. Hasil latensi dan error

### 3.1 Uji 1 (11:34:32–11:35:37 WIB)

```text
[SEMUA] permintaan=522  rps=8.70  sukses=522  5xx=0  gagal_koneksi=0  error_rate=0.00%
         p50=568 ms  p95=726 ms  p99=744 ms  maks=758 ms  rata2=578 ms
[/] permintaan=262  rps=4.37  sukses=262  5xx=0  gagal_koneksi=0  error_rate=0.00%
         p50=599 ms  p95=730 ms  p99=754 ms  maks=758 ms  rata2=592 ms
[/api/info] permintaan=130  rps=2.17  sukses=130  5xx=0  gagal_koneksi=0  error_rate=0.00%
         p50=538 ms  p95=712 ms  p99=731 ms  maks=740 ms  rata2=567 ms
[/health] permintaan=130  rps=2.17  sukses=130  5xx=0  gagal_koneksi=0  error_rate=0.00%
         p50=533 ms  p95=709 ms  p99=735 ms  maks=744 ms  rata2=559 ms
Status HTTP: {200: 522}
Data mentah: loadtest-20261111-113537.csv
```

### 3.2 Uji 2 (11:37:02–11:38:08 WIB, dengan pemantauan server)

```text
[SEMUA] permintaan=535  rps=8.92  sukses=535  5xx=0  gagal_koneksi=0  error_rate=0.00%
         p50=538 ms  p95=689 ms  p99=934 ms  maks=957 ms  rata2=562 ms
[/] permintaan=265  rps=4.42  sukses=265  5xx=0  gagal_koneksi=0  error_rate=0.00%
         p50=544 ms  p95=745 ms  p99=952 ms  maks=957 ms  rata2=568 ms
[/api/info] permintaan=135  rps=2.25  sukses=135  5xx=0  gagal_koneksi=0  error_rate=0.00%
         p50=549 ms  p95=689 ms  p99=774 ms  maks=850 ms  rata2=568 ms
[/health] permintaan=135  rps=2.25  sukses=135  5xx=0  gagal_koneksi=0  error_rate=0.00%
         p50=521 ms  p95=664 ms  p99=735 ms  maks=744 ms  rata2=542 ms
Status HTTP: {200: 535}
Data mentah: loadtest-20261111-113808.csv
```

### 3.3 Ringkasan

| Ukuran | Uji 1 | Uji 2 |
|---|---|---|
| Total permintaan | 522 | 535 |
| Throughput | 8,70 req/s | 8,92 req/s |
| p50 / p95 / p99 semua halaman | 568 / 726 / 744 ms | 538 / 689 / 934 ms |
| **p95 halaman materi `/`** | **730 ms** | **745 ms** |
| Maksimum | 758 ms | 957 ms |
| Error (5xx + gagal koneksi) | 0 (0,00%) | 0 (0,00%) |

## 4. Pemakaian sumber daya server

### 4.1 Kondisi diam (tanpa beban, 11:29–11:34 WIB)

```text
               total        used        free      shared  buff/cache   available
Mem:             887         265         120           3         527         621
Swap:           1023           0        1023
    PID   RSS %CPU COMMAND
    922 30260  0.0 .../gunicorn --workers 1 --threads 2 --bind 127.0.0.1:8000 app:app
    727 26616  0.0 .../gunicorn --workers 1 --threads 2 --bind 127.0.0.1:8000 app:app
/dev/root        29G  4.0G   25G  14% /
```

CPU idle 99–100% sepanjang dua rekaman (masing-masing 24 sampel × 5 detik).

### 4.2 Selama uji 2 (perekam berjalan di VM sejak 11:36:32 WIB, sampel tiap 5 detik)

```text
== MULAI
Wed Nov 11 11:36:32 WIB 2026
               total        used        free      shared  buff/cache   available
Mem:             887         271         115           3         527         616
Swap:           1023           0        1023
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st gu
 0  0      0    114     21    505    0    0   514    34  237    1  1  0 99  0  0  0
 0  0      0    116     21    505    0    0     0     2  171  101  0  0 100  0  0  0
 0  0      0    117     21    505    0    0     0     1  146   80  0  0 100  0  0  0
 0  0      0    117     21    505    0    0     0     1  169   93  0  0 100  0  0  0
 0  0      0    117     21    505    0    0     0     1  153   80  0  0 100  0  0  0
 0  0      0    117     21    505    0    0     0     0  139   75  0  0 100  0  0  0
 0  0      0    117     21    505    0    0     0     1  156   83  0  0 100  0  0  0
 0  0      0    117     21    505    0    0     0   110  571  575  1  0 99  0  0  0
 0  0      0    117     21    505    0    0     0     2  471  504  1  0 99  0  0  0
 0  0      0    117     21    505    0    0     0     1  476  507  1  0 99  0  0  0
 0  0      0    117     21    505    0    0     0     0  640  809  1  1 98  0  0  0
 0  0      0    117     21    505    0    0     0     1  553  567  1  0 99  0  0  0
 0  0      0    117     21    505    0    0     0     1  519  514  1  0 99  0  0  0
 0  0      0    117     21    505    0    0     0    51  604  612  1  0 99  0  0  0
 0  0      0    117     21    505    0    0     0     2  574  596  1  0 99  0  0  0
 0  0      0    116     22    505    0    0    94     1  639  676  1  1 98  1  0  0
 0  0      0    116     22    505    0    0     0     0  510  525  1  0 99  0  0  0
 0  0      0    116     22    505    0    0     0     1  636  644  1  0 99  0  0  0
 0  0      0    116     22    505    0    0     0     1  590  607  1  0 99  0  0  0
 0  0      0    116     22    505    0    0     0    15  602  609  1  0 99  0  0  0
 0  0      0    116     22    505    0    0     0     1  193  133  0  0 100  0  0  0
 0  0      0    116     22    505    0    0     0    42  158   85  0  0 100  0  0  0
 0  0      0    116     22    505    0    0     0     0  230  287  0  0 100  0  0  0
```

Baris dengan `in`/`cs` sekitar 500–800 (sampel ke-8 sampai ke-20, sekitar 11:37:07–11:38:07 WIB) adalah periode uji beban; selebihnya kondisi diam. Berkas rekaman dibaca sebelum perekam selesai (23 dari 30 sampel), sehingga blok penutup tidak ikut; periode uji sudah tercakup penuh.

### 4.3 Ringkasan sumber daya

| Ukuran | Diam | Selama beban | Batas | Status |
|---|---|---|---|---|
| CPU terpakai (us + sy) | 0–1% | maksimum 2% | — | Sangat longgar |
| RAM terpakai (`free -m`) | 263–265 MiB dari 887 MiB (±30%) | 271 MiB saat mulai (30,6%); `free` vmstat tetap 116–117 MiB, tanpa penurunan selama beban | ≤ 80% | LULUS |
| Swap terpakai | 0 | 0 | — | — |
| RSS Gunicorn (2 proses) | 30,3 MiB + 26,6 MiB | (tidak berubah berarti) | — | — |
| Disk `/` | 14% (4,0 GiB dari 29 GiB) | 14% | ≤ 50% | LULUS |

## 5. Penafsiran

1. **Latensi didominasi jaringan, bukan server.** `/health` (hampir tanpa pemrosesan) memiliki p50 521–533 ms, hampir sama dengan halaman materi `/` (544–599 ms). Selisih sekitar 20–70 ms adalah waktu pemrosesan halaman; sisanya waktu tempuh Indonesia ↔ Australia East ditambah jabat tangan TLS di setiap permintaan.
2. **Server hampir tidak terbebani.** CPU maksimum 2% dan RAM tidak naik selama 5 pengguna bersamaan, sehingga kredit CPU burstable (baseline 20%) tidak terpakai.
3. **Throughput dibatasi klien.** Dengan 5 pengguna yang menunggu respons sekitar 0,56 detik, throughput maksimum yang dapat dihasilkan klien sekitar 5 ÷ 0,56 ≈ 9 req/s, sesuai hasil 8,7–8,9 req/s. Uji ini **tidak** menemukan batas kapasitas server.
4. p99 uji 2 (934 ms) lebih tinggi dari uji 1 (744 ms) karena beberapa permintaan lambat; konsisten dengan variasi jaringan hotspot ponsel.

## 6. Hasil terhadap kriteria

| Kriteria | Batas | Hasil | Status |
|---|---|---|---|
| NFR-04: p95 halaman materi, 5 pengguna, dari Indonesia | ≤ 2.000 ms | 730 ms (uji 1), 745 ms (uji 2) | **LULUS** |
| Error rate 5xx | < 1% | 0,00% (1.057 permintaan) | **LULUS** |
| NFR-05: RAM puncak | ≤ 80% | ±31% | **LULUS** |
| NFR-05: disk | ≤ 50% | 14% | **LULUS** |

## 7. Batasan dan isu tersisa

1. **Halaman kuis dan cek risiko (FR-02, FR-06) belum ada**; yang diuji hanya halaman materi M03 dan endpoint informasi. NFR-04 untuk halaman kuis dan FR-06 (≤ 3 detik) diuji ulang pada M11.
2. **Hanya 5 pengguna bersamaan.** Tidak ada klaim kapasitas di atas 5 pengguna; batas kapasitas server belum dicari.
3. **Satu klien dengan hotspot ponsel.** Hasil dapat berbeda pada jaringan sekolah atau WiFi; tidak ada uji dari banyak lokasi.
4. **Tanpa keep-alive.** Peramban nyata memakai ulang koneksi sehingga latensi pengguna kemungkinan lebih rendah; hasil ini merupakan batas atas yang konservatif.
5. Data aplikasi masih `cases.json` (tanpa database); setelah SQLite dipakai (M05), uji diulang.

## 8. Berkas pendukung (folder `docs/evidence/ev08/`)

| Berkas | Isi |
|---|---|
| `loadtest.py` | Skrip uji beban yang dipakai |
| `loadtest-20261111-113537.csv` | Data mentah uji 1 (522 baris) |
| `loadtest-20261111-113808.csv` | Data mentah uji 2 (535 baris) |
