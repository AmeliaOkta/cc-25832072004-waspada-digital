# ADR-0003: Backup SQLite ke Azure Blob privat dengan Managed Identity

| Item | Isi |
|---|---|
| Status | Accepted (09-11-2026) |
| Tanggal | 09-11-2026; diperbarui 10-11-2026 (retensi diterapkan) |
| Penulis | Amelia Okta Ramadani (25832072004) |
| Terkait | Temuan audit 01 dan 02; `docs/evidence/ev05-backup.md`; `docs/evidence/ev06-restore.md`; ADR-0001 |

## Konteks

- Database SQLite (`cloudlits.db`) akan menyimpan skor kuis; target RPO ≤ 24 jam, RTO ≤ 60 menit.
- Backup harus berada **di luar VM**, dengan akses terbatas, terjadwal, dilengkapi checksum dan manifest, serta dapat dipulihkan (Temuan 01 dan 02).
- Anggaran berasal dari kredit Azure for Students; tidak ada dana untuk layanan backup berbayar besar.
- Tidak boleh ada secret (access key, SAS token) yang tersimpan di server.

## Keputusan

1. Backup dibuat dengan **`sqlite3 .backup`** (Online Backup API), bukan `cp`, agar konsisten walau database sedang dipakai.
2. Setiap backup menghasilkan berkas `.db`, `.sha256`, dan `.manifest.json` (ukuran, SHA-256, `integrity_check`, jumlah baris, metode).
3. Berkas diunggah ke **Azure Blob Storage** `cloudlitsbackupamel`, container privat `sqlite-backups`, folder `harian/`.
4. VM mengunggah memakai **Managed Identity (system-assigned)** dengan role *Storage Blob Data Contributor* **hanya pada scope container**; tidak ada secret di server.
5. Jadwal: `cloudlits-backup.timer` setiap hari **02:00 WIB** dengan `Persistent=true` (backup disusulkan bila VM mati pada jam jadwal).
6. Retensi **14 hari** lewat lifecycle management rule `hapus-backup-14-hari` (diterapkan 10-11-2026).
7. Pemulihan memakai `restore-sqlite.sh` (menolak menimpa database yang ada; verifikasi checksum, integritas, dan jumlah baris sebelum memindahkan berkas).

## Alternatif yang dipertimbangkan

| Alternatif | Alasan tidak dipilih |
|---|---|
| Salinan di disk VM yang sama | Tidak off-site; hilang bersama VM |
| Azure Backup (Recovery Services vault) untuk seluruh VM | Biaya lebih besar; tidak memberi backup konsisten pada tingkat database |
| Snapshot managed disk | Biaya per snapshot; satu disk, bukan per database |
| Akses dengan access key atau SAS token | Secret harus disimpan di server |
| Database terkelola (Azure SQL/PostgreSQL) | Biaya dan di luar kebutuhan (ADR-0001) |

## Konsekuensi

- Positif: biaya penyimpanan sangat kecil (estimasi batas atas USD 0,14/bulan); tanpa secret; restore terbukti di VM yang sama dan di lingkungan terpisah (ev06).
- Negatif: backup hanya berjalan saat VM menyala; RPO efektif bergantung pada selang penyalaan VM.
- Checksum dan manifest disimpan di tempat yang sama dengan backup, sehingga tidak melindungi dari perubahan semua berkas sekaligus.
- Akses jaringan storage dibiarkan `Allow` agar backup dapat diambil tanpa VM; mitigasi: tanpa akses anonim, wajib autentikasi, HTTPS-only, TLS 1.2.

## Kondisi peninjauan ulang

- Saat aplikasi mulai memakai SQLite untuk data siswa nyata (M05).
- Bila data siswa nyata disimpan: tinjau pembatasan jaringan storage dan enkripsi tambahan.
- Uji rebuild VM penuh dan RTO end-to-end pada M12.

## Bukti

`docs/evidence/ev05-backup.md` dan `docs/evidence/ev06-restore.md`.
