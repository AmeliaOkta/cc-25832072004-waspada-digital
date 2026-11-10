# EV-PENUNJANG — Perbedaan Kapasitas dan Biaya terhadap Acuan 1/1/20 (Temuan 07)

| Item | Isi |
|---|---|
| Proyek | CloudLits — CC-PTI2802-25832072004-CLOUDLITS |
| Mahasiswa | Amelia Okta Ramadani (25832072004) |
| Temuan audit | 07 — Disk nyata 30 GB berbeda dari baseline praktikum 20 GB (baris 83) |
| Kriteria uji | Tabel delta spesifikasi dan biaya akurat, tanpa menganggap batas kelas terpenuhi |
| Data | Pengukuran 08-11-2026 (portal, kalkulator, terminal VM) dan 10-11-2026 (Azure CLI, Run Command) |
| Status | **LULUS** untuk tabel delta dan alasan kapasitas; spesifikasi aktual tetap **melebihi** acuan dan tidak diklaim memenuhi batas kelas |

> Berkas ini tidak memuat secret, Subscription ID, atau data siswa. Spesifikasi lengkap dan output mentah ada di `ev01-vps-spec.md`.

## 1. Spesifikasi terukur (identitas versi)

| Parameter | Nilai | Bukti |
|---|---|---|
| VM | `VpsAmel`, hostname `cc-m03-25832072004` | ev01 bagian 1 |
| SKU | `Standard_B2ats_v2` | `az vm show` (10-11-2026) |
| vCPU | 2 (`nproc`), AMD EPYC 7763, **1 socket, 2 thread per core** | `lscpu` (10-11-2026) |
| RAM | 887 MiB terbaca dari 1 GiB + swap 1 GiB | `free -h` (08-11 dan 10-11-2026) |
| OS disk | 30 GiB, Premium SSD LRS, tier P4, `FromImage` | `lsblk`, `az disk list` (10-11-2026); portal Disks (08-11-2026) |
| Root | 29 GiB, terpakai 4,0 GiB (14%) | `df -h /` (10-11-2026) |
| OS | Ubuntu 24.04.5 LTS, kernel 7.0.0-1017-azure | `/etc/os-release` (10-11-2026) |

## 2. Tabel delta spesifikasi

| Parameter | Acuan praktikum 1/1/20 | Aktual (B2ats v2) | Delta | Penjelasan |
|---|---|---|---|---|
| vCPU | 1 | 2 | +1 vCPU | Dua vCPU berasal dari 1 core fisik dengan 2 thread (SMT). Kinerja dasar dijamin hanya 20% (burstable, sistem kredit CPU) |
| RAM | 1 GB | 1 GiB (887 MiB terbaca) | ≈ 0 | Sama dengan acuan; batas utama aplikasi tetap RAM |
| Disk | 20 GB | 30 GiB | +10 GiB | Ukuran bawaan image `ubuntu-24_04-lts` (`FromImage`); tidak diubah saat VM dibuat |
| Tier disk | P4 (32 GiB) | P4 (32 GiB) | sama | Disk 20 GB juga jatuh di tier P4 (tier P3 hanya 16 GiB), sehingga biaya disk sama |
| IPv4 publik | 1 | 1 (Static) | 0 | — |
| OS | Ubuntu 24.04 | Ubuntu 24.04.5 LTS | 0 | — |

## 3. Kinerja CPU burstable

Menurut Microsoft Learn (Basv2-series, diakses 10-11-2026), `Standard_B2ats_v2` memiliki base CPU performance **20%**, initial credits 60, credits banked 24 per jam, dan maksimum 576 kredit. Bila kredit habis, VM diturunkan kembali ke kinerja dasar 20%.

Sumber: https://learn.microsoft.com/azure/virtual-machines/sizes/general-purpose/basv2-series

Penafsiran: "2 vCPU" pada SKU ini tidak berarti dua kali kemampuan VM 1 vCPU tetap. Untuk beban berkelanjutan, kapasitas yang dijamin lebih kecil daripada satu core penuh. Karena itu tambahan vCPU **tidak dipakai sebagai alasan** untuk mengklaim kapasitas pengguna; kapasitas tetap harus diukur lewat uji beban (ev08, M11).

## 4. Tabel delta biaya (bruto, sebelum kredit)

Sumber tarif: kalkulator harga Azure, region Australia East, Linux Ubuntu, Pay as you go, 730 jam/bulan, USD, dihitung 08-11-2026.

| Komponen | Pembanding 1/1/20 (B1s) | Aktual (B2ats v2) | Delta per bulan |
|---|---|---|---|
| Compute | USD 9,64 | USD 8,69 | −USD 0,95 |
| Disk (P4, 32 GiB) | USD 5,28 | USD 5,28 | USD 0,00 |
| **Subtotal VM + disk** | **USD 14,92** | **USD 13,97** | **−USD 0,95** |
| Public IPv4 Static Standard | USD 3,65 | USD 3,65 | USD 0,00 |
| Blob backup (batas atas) | USD 0,14 | USD 0,14 | USD 0,00 |
| **Total bruto** | **USD 18,71** | **USD 17,76** | **−USD 0,95** |

Catatan:

1. **SKU pembanding B1s dipilih sendiri** karena modul praktikum tidak menyebut SKU Azure untuk VM acuan 1/1/20. Angka pembanding bukan data dosen.
2. Biaya nyata yang ditagih lebih rendah dari bruto: pada Cost analysis 1 Sep–9 Nov 2026, meter "B2ats v2 – Free" membuat compute bernilai USD 0,00 (rincian dan sumber di ev07). Penghematan ini milik langganan Azure for Students, bukan keunggulan SKU.
3. Tambahan disk +10 GiB **tidak menambah biaya** karena acuan 20 GB pun dibulatkan ke tier P4.

## 5. Kesimpulan

| Pertanyaan | Jawaban |
|---|---|
| Apakah spesifikasi aktual sama dengan acuan 1/1/20? | **Tidak.** Melebihi pada vCPU (+1) dan disk (+10 GiB); RAM sama |
| Apakah selisih menambah biaya? | **Tidak.** Disk sama di tier P4; compute B2ats v2 lebih murah USD 0,95/bulan dibanding pembanding B1s |
| Mengapa disk 30 GiB? | Ukuran bawaan image Ubuntu 24.04 (`FromImage`), tidak diubah saat pembuatan VM |
| Apakah batas kelas dianggap terpenuhi? | **Tidak diklaim.** Selisih dijelaskan dan dicatat di laporan (6.2, Tabel 6.2b, 11.3); keputusan penerimaan oleh dosen |
| Apakah kelebihan spesifikasi mengubah klaim kapasitas? | Tidak. Kapasitas pengguna hanya diklaim dari hasil uji beban (ev08) |

## 6. Isu tersisa

1. SKU pembanding (B1s) adalah pilihan mahasiswa; dosen dapat menetapkan pembanding lain.
2. Mengecilkan disk ke 20 GB tidak dilakukan: Azure tidak mendukung pengecilan managed disk, dan biayanya tidak berubah (tier P4 sama).
3. Tangkapan layar portal Disks (08-11-2026, `01-portal-os-disk.png`) belum dilampirkan; data yang sama dibuktikan lewat Azure CLI di ev01.
