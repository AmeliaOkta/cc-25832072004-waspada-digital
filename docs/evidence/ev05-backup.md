# EV-05 — Backup SQLite Off-site (Temuan 01, P0)

| Item | Isi |
|---|---|
| Proyek | CloudLits — CC-PTI2802-25832072004-CLOUDLITS |
| Mahasiswa | Amelia Okta Ramadani (25832072004) |
| Temuan audit | 01 — Lokasi penyimpanan backup eksternal/off-site (baris 90) |
| Waktu pengumpulan bukti | 10-11-2026, 21:06–21:34 WIB |
| Status | **LULUS** untuk kriteria uji Temuan 01, dengan isu tersisa pada bagian 9 |

> Berkas ini tidak memuat password, access key, SAS token, connection string, Subscription ID, atau data siswa.
> Database yang dibackup berisi **data sintetis** (30 pengguna, 90 percobaan kuis), bukan data siswa nyata.

## 1. Tujuan dan kriteria uji (dari arahan dosen)

| Kriteria | Sumber arahan |
|---|---|
| Backup tersimpan di lokasi terpisah dari VM dengan izin terbatas dan enkripsi | Temuan 01 — Perbaikan |
| Ada manifest, jadwal, dan checksum | Temuan 01 — Kriteria uji |
| Retensi ditetapkan | Temuan 01 — Perbaikan |
| Berkas backup off-VM dapat ditemukan tanpa login ke VM sumber dan checksum cocok | Bagian III.3 — Bukti lulus |
| Backup konsisten (bukan `cp` berkas yang sedang ditulis) | Bagian IV.3 |

## 2. Metode pengumpulan bukti

| Langkah | Alat | Keterangan |
|---|---|---|
| Menyalakan VM | Azure Cloud Shell: `az vm start` | Tombol *Start* di Portal gagal tanpa pesan error (Activity log kosong); lewat CLI berhasil. Status: `VM running`. |
| Konfigurasi storage, retensi, daftar blob, checksum | Azure Cloud Shell (Azure CLI), di luar VM | Tidak ada login ke VM. |
| Konfigurasi timer, status service, log | `az vm run-command invoke` (Azure Run Command, dijalankan sebagai root lewat agen VM) | SSH tidak dipakai karena laptop yang digunakan tidak memiliki key yang terdaftar di VM. |

## 3. Lokasi dan kontrol akses

Perintah:

```bash
az storage account show -n cloudlitsbackupamel -g AmeliaOkta_ --query "{name:name, location:location, sku:sku.name, accessTier:accessTier, allowBlobPublicAccess:allowBlobPublicAccess, httpsOnly:enableHttpsTrafficOnly, minimumTlsVersion:minimumTlsVersion, blobEncryption:encryption.services.blob.enabled, keySource:encryption.keySource, networkDefaultAction:networkRuleSet.defaultAction}" -o json
```

```json
{
  "accessTier": "Hot",
  "allowBlobPublicAccess": false,
  "blobEncryption": true,
  "httpsOnly": true,
  "keySource": "Microsoft.Storage",
  "location": "australiaeast",
  "minimumTlsVersion": "TLS1_2",
  "name": "cloudlitsbackupamel",
  "networkDefaultAction": "Allow",
  "sku": "Standard_LRS"
}
```

```bash
az storage container-rm show --storage-account cloudlitsbackupamel -g AmeliaOkta_ -n sqlite-backups --query "{container:name, publicAccess:publicAccess}" -o json
```

```json
{
  "container": "sqlite-backups",
  "publicAccess": "None"
}
```

Identitas yang menulis backup (Managed Identity VM), Subscription ID disamarkan:

```bash
az vm show -g AmeliaOkta_ -n VpsAmel --query "identity.type" -o tsv
az role assignment list --assignee "$PRINCIPAL" --all --query "[].{role:roleDefinitionName, scope:scope}" -o json
```

```text
SystemAssigned
[
  {
    "role": "Storage Blob Data Contributor",
    "scope": "/subscriptions/<disamarkan>/resourceGroups/AmeliaOkta_/providers/Microsoft.Storage/storageAccounts/cloudlitsbackupamel/blobServices/default/containers/sqlite-backups"
  }
]
```

Ringkasan:

| Parameter | Nilai | Penilaian |
|---|---|---|
| Layanan | Azure Blob Storage, storage account `cloudlitsbackupamel` (Australia East, Standard_LRS, Hot) | Terpisah dari disk VM |
| Container | `sqlite-backups`, `publicAccess: None` | Privat |
| Akses anonim akun | `allowBlobPublicAccess: false` | Tidak ada akses anonim |
| Identitas penulis | Managed Identity VM (SystemAssigned), satu-satunya role: *Storage Blob Data Contributor* pada **scope container** | Hak akses minimum; tidak ada secret di server |
| Enkripsi | Enkripsi sisi server aktif (`keySource: Microsoft.Storage`, kunci dikelola Microsoft) | Sesuai untuk data sintetis/pseudonim |
| Transport | HTTPS saja, TLS minimum 1.2 | Aman saat transfer |
| Jaringan | `networkDefaultAction: Allow` | Lihat keputusan di bagian 9 |

## 4. Retensi (lifecycle management)

Aturan dipasang lewat Azure CLI karena menu *Lifecycle management* di Portal gagal dimuat ("The Essentials component encountered an error while loading").

```bash
az storage account management-policy show --account-name cloudlitsbackupamel -g AmeliaOkta_ --query "{storageAccount:'cloudlitsbackupamel', lastModifiedTime:lastModifiedTime, rules:policy.rules[].{name:name, enabled:enabled, deleteAfterDaysSinceModified:definition.actions.baseBlob.delete.daysAfterModificationGreaterThan, prefix:definition.filters.prefixMatch, blobTypes:definition.filters.blobTypes}}" -o json
```

```json
{
  "lastModifiedTime": "2026-11-10T14:10:53.838194+00:00",
  "rules": [
    {
      "blobTypes": [
        "blockBlob"
      ],
      "deleteAfterDaysSinceModified": 14.0,
      "enabled": true,
      "name": "hapus-backup-14-hari",
      "prefix": [
        "sqlite-backups/"
      ]
    }
  ],
  "storageAccount": "cloudlitsbackupamel"
}
```

| Parameter | Nilai |
|---|---|
| Retensi | 14 hari sejak terakhir diubah |
| Rule | `hapus-backup-14-hari`, enabled |
| Cakupan | Semua block blob di container `sqlite-backups` (folder `harian/` dan `uji/`) |
| Diterapkan | 10-11-2026 21:10:53 WIB (`lastModifiedTime` 2026-11-10T14:10:53Z) |
| Catatan | Azure menjalankan lifecycle policy secara berkala, bukan seketika. Penghapusan pertama baru dapat diamati setelah ada blob berumur lebih dari 14 hari (paling cepat sekitar 23-11-2026 untuk blob tanggal 09-11-2026). |

## 5. Jadwal backup (systemd timer)

Isi unit (diambil dengan `systemctl cat cloudlits-backup.timer cloudlits-backup.service`). Tidak memuat secret.

```ini
# /etc/systemd/system/cloudlits-backup.timer
[Unit]
Description=Jadwal backup harian SQLite CloudLits (02:00 WIB)

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true
Unit=cloudlits-backup.service

[Install]
WantedBy=timers.target

# /etc/systemd/system/cloudlits-backup.service
[Unit]
Description=Backup harian SQLite CloudLits ke Azure Blob
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=azureuseramel
ExecStart=/home/azureuseramel/cloudlits-data/backup-sqlite.sh
```

Zona waktu VM: `Asia/Jakarta (WIB, +0700)`, sehingga `02:00:00` berarti 02:00 WIB.

```text
NEXT                        LEFT     LAST                        PASSED     UNIT                    ACTIVATES
Wed 2026-11-11 02:00:00 WIB 4h 31min Tue 2026-11-10 21:05:50 WIB 22min ago  cloudlits-backup.timer  cloudlits-backup.service
```

### 5.1 Bukti timer terpicu sendiri (bukan dijalankan manual)

VM dalam keadaan *Stopped (deallocated)* pada jadwal 02:00 WIB tanggal 10-11-2026. Setelah VM dinyalakan, timer (`Persistent=true`) menjalankan backup yang terlewat tanpa perintah manual.

```text
== BOOT ==
2026-11-10 21:05:37
== TIMER LAST TRIGGER ==
NextElapseUSecRealtime=Wed 2026-11-11 02:00:00 WIB
LastTriggerUSec=Tue 2026-11-10 21:05:50 WIB
== SERVICE RESULT ==
Result=success
ExecMainStartTimestamp=Tue 2026-11-10 21:05:50 WIB
ExecMainExitTimestamp=Tue 2026-11-10 21:05:51 WIB
ExecMainStatus=0
```

| Waktu (WIB) | Kejadian |
|---|---|
| 21:05:37 | VM selesai boot |
| 21:05:50 | `cloudlits-backup.timer` memicu service (`LastTriggerUSec`), 13 detik setelah boot |
| 21:05:51 | Service selesai, `Result=success`, exit code 0 |
| 11-11-2026 02:00 | Jadwal berikutnya |

### 5.2 Log eksekusi

```text
2026-11-10T21:05:50+07:00 cc-m03-25832072004 systemd[1]: Starting cloudlits-backup.service - Backup harian SQLite CloudLits ke Azure Blob...
2026-11-10T21:05:50+07:00 cc-m03-25832072004 backup-sqlite.sh[971]: 2026-11-10T14:05:50Z MULAI backup cloudlits-20261110T140550Z.db
2026-11-10T21:05:51+07:00 cc-m03-25832072004 backup-sqlite.sh[1075]: 2026-11-10T14:05:51Z UNGGAH cloudlits-20261110T140550Z.db HTTP 201
2026-11-10T21:05:51+07:00 cc-m03-25832072004 backup-sqlite.sh[1086]: 2026-11-10T14:05:51Z UNGGAH cloudlits-20261110T140550Z.db.sha256 HTTP 201
2026-11-10T21:05:51+07:00 cc-m03-25832072004 backup-sqlite.sh[1090]: 2026-11-10T14:05:51Z UNGGAH cloudlits-20261110T140550Z.db.manifest.json HTTP 201
2026-11-10T21:05:51+07:00 cc-m03-25832072004 backup-sqlite.sh[1093]: 2026-11-10T14:05:51Z SELESAI backup cloudlits-20261110T140550Z.db sha256=dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044
2026-11-10T21:05:51+07:00 cc-m03-25832072004 systemd[1]: cloudlits-backup.service: Deactivated successfully.
2026-11-10T21:05:51+07:00 cc-m03-25832072004 systemd[1]: Finished cloudlits-backup.service - Backup harian SQLite CloudLits ke Azure Blob.
```

### 5.3 Pemeriksaan secret pada skrip

```bash
grep -n -i -E 'accountkey|account_key|sas|sig=|password|connectionstring|connection_string' /home/azureuseramel/cloudlits-data/backup-sqlite.sh || echo 'tidak ada pola secret'
```

```text
tidak ada pola secret
```

Izin berkas di VM: folder `cloudlits-data` `drwx------` (700), `cloudlits.db` `-rw-------` (600), skrip `-rwx------` (700); pemilik `azureuseramel`.

## 6. Bukti penyimpanan terpisah (tanpa login ke VM)

Daftar blob diambil dari Azure Cloud Shell, bukan dari VM:

```text
Name                                                Bytes    LastModified
--------------------------------------------------  -------  -------------------------
harian/cloudlits-20261109T094851Z.db                24576    2026-11-09T09:49:53+00:00
harian/cloudlits-20261109T094851Z.db.sha256         96       2026-11-09T09:49:53+00:00
harian/cloudlits-20261109T095706Z.db                24576    2026-11-09T09:57:06+00:00
harian/cloudlits-20261109T095706Z.db.manifest.json  348      2026-11-09T09:57:06+00:00
harian/cloudlits-20261109T095706Z.db.sha256         96       2026-11-09T09:57:06+00:00
harian/cloudlits-20261109T101910Z.db                24576    2026-11-09T10:19:10+00:00
harian/cloudlits-20261109T101910Z.db.manifest.json  348      2026-11-09T10:19:10+00:00
harian/cloudlits-20261109T101910Z.db.sha256         96       2026-11-09T10:19:10+00:00
harian/cloudlits-20261110T140550Z.db                24576    2026-11-10T14:05:51+00:00
harian/cloudlits-20261110T140550Z.db.manifest.json  348      2026-11-10T14:05:51+00:00
harian/cloudlits-20261110T140550Z.db.sha256         96       2026-11-10T14:05:51+00:00
uji/uji-unggah.txt                                  45       2026-11-09T09:36:57+00:00
```

Catatan: tiga backup tanggal 09-11-2026 adalah uji manual saat penyiapan (Revisi 01); backup pertama (`094851Z`) dibuat sebelum manifest ditambahkan ke skrip. Backup `20261110T140550Z` dipicu oleh timer.

## 7. Manifest dan checksum

Sampel: backup terbaru yang dipicu timer. Ketiga berkas diunduh dari Blob ke Azure Cloud Shell, lalu hash dihitung ulang di sana.

```text
-rw-r--r-- 1 amelia amelia 24576 Nov 10 14:18 cloudlits-20261110T140550Z.db
-rw-r--r-- 1 amelia amelia   348 Nov 10 14:18 cloudlits-20261110T140550Z.db.manifest.json
-rw-r--r-- 1 amelia amelia    96 Nov 10 14:18 cloudlits-20261110T140550Z.db.sha256
--- hash dihitung ulang di Cloud Shell ---
dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044  cloudlits-20261110T140550Z.db
--- isi .sha256 dari Blob ---
dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044  cloudlits-20261110T140550Z.db
```

Isi manifest:

```json
{
  "berkas": "cloudlits-20261110T140550Z.db",
  "waktu_utc": "20261110T140550Z",
  "ukuran_byte": 24576,
  "sha256": "dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044",
  "integrity_check": "ok",
  "baris": {"pengguna": 30, "percobaan_kuis": 90},
  "versi_sqlite_cli": "3.45.1",
  "metode": "sqlite3 .backup (Online Backup API)"
}
```

| Sumber hash | SHA-256 | Cocok |
|---|---|---|
| Log VM saat backup (`SELESAI ... sha256=`) | `dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044` | — |
| Berkas `.sha256` di Blob | `dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044` | YA |
| Manifest di Blob | `dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044` | YA |
| Dihitung ulang di Cloud Shell (di luar VM) | `dcbd89331907e5e23f3d40e612fb5d8d0ae50e33122a421d5475e944d5008044` | YA |

## 8. Hasil

| Kriteria | Expected | Actual | Status |
|---|---|---|---|
| Lokasi terpisah dari VM | Blob privat di luar disk VM | Azure Blob `cloudlitsbackupamel/sqlite-backups`, `publicAccess: None` | LULUS |
| Akses minimum, tanpa secret | Managed Identity hanya di scope container; skrip tanpa secret | Satu role *Storage Blob Data Contributor* di scope container; `tidak ada pola secret` | LULUS |
| Enkripsi | Enkripsi at-rest dan in-transit aktif | SSE aktif, HTTPS-only, TLS 1.2 | LULUS |
| Jadwal otomatis | Timer memicu service tanpa campur tangan | `LastTriggerUSec` 21:05:50 WIB, `Result=success`, jadwal berikutnya 02:00 WIB | LULUS |
| Backup konsisten | Online Backup API, bukan `cp` | `sqlite3 .backup (Online Backup API)`, `integrity_check: ok` | LULUS |
| Manifest + SHA-256 | Ada dan cocok setelah diambil dari Blob | 4 sumber hash identik | LULUS |
| Retensi diterapkan | Lifecycle rule 14 hari aktif | `hapus-backup-14-hari`, enabled, sejak 10-11-2026 21:10 WIB | LULUS (penghapusan pertama belum teramati) |
| Ditemukan tanpa login ke VM | Daftar dan unduh blob dari luar VM | Daftar blob dan unduhan dilakukan dari Azure Cloud Shell | LULUS |

## 9. Isu tersisa dan keputusan

1. **Aplikasi belum memakai SQLite.** Aplikasi masih membaca `cases.json`; backup diuji pada database `cloudlits.db` berisi data sintetis. Mekanisme backup terbukti, tetapi belum untuk data aplikasi yang sebenarnya (integrasi pada M05).
2. **Jadwal persis 02:00 WIB dengan VM menyala belum teramati.** Yang terbukti adalah eksekusi oleh timer melalui mekanisme susulan (`Persistent=true`) setelah VM menyala. Karena VM sering dimatikan di luar sesi, backup terjadi saat VM berikutnya menyala; RPO efektif = selang antar-penyalaan VM, bukan 24 jam. Selama belum ada data siswa nyata, kondisi ini diterima.
3. **Akses jaringan Storage `Allow` (keputusan sadar).** Akses jaringan publik tidak dibatasi ke subnet VM agar backup tetap dapat diambil tanpa login ke VM (Cloud Shell/laptop) saat VM rusak atau hilang. Mitigasi: tanpa akses anonim, wajib autentikasi Microsoft Entra ID atau kunci akun, HTTPS-only, TLS 1.2. Ditinjau ulang bila data siswa nyata mulai disimpan.
4. **Penghapusan oleh lifecycle belum teramati.** Diperiksa ulang setelah 23-11-2026 dengan `az storage blob list`; blob tanggal 09-11-2026 seharusnya sudah terhapus.
5. **Salinan lokal di folder `staging` di VM menumpuk** (128 KB per 10-11-2026). Belum ada pembersihan otomatis; ditambahkan ke skrip atau dibersihkan manual pada M05.
6. **Tombol Start VM di Portal gagal tanpa pesan error** (10-11-2026); dicatat di runbook: gunakan `az vm start -g AmeliaOkta_ -n VpsAmel` dari Cloud Shell sebagai jalur cadangan.
