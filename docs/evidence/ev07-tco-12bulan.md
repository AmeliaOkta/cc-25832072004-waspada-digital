# EV-07 — TCO 12 Bulan, Kredit Azure for Students, dan Budget Alert (Temuan 05)

| Item | Isi |
|---|---|
| Proyek | CloudLits — CC-PTI2802-25832072004-CLOUDLITS |
| Mahasiswa | Amelia Okta Ramadani (25832072004) |
| Temuan audit | 05 — Manfaat kredit Azure for Students tidak sama dengan tarif VM gratis permanen (baris 89) |
| Kriteria uji | Masa aktif sesuai kredit, tersedia budget alert, serta keputusan stop/upgrade |
| Waktu verifikasi | Tarif: 09-11-2026. Biaya aktual: 09-11-2026. Kredit dan budget: 10-11-2026 22:40 WIB |
| Status | **LULUS** untuk kredit, burn-rate, budget alert, dan keputusan setelah kredit; tarif tetap **estimasi** |

> Berkas ini tidak memuat Subscription ID, email, nomor kartu, atau data siswa. Semua angka dalam **USD**; tidak ada konversi kurs (kredit dan tagihan Azure for Students dalam USD).

## 1. Sumber data

| Data | Sumber | Tanggal |
|---|---|---|
| Tarif bruto | Azure Pricing Calculator, ekspor `azure-pricing-estimate-2026-11-09.xlsx` (Australia East, Linux, Pay as you go, 730 jam/bulan, program Microsoft Customer Agreement) | 09-11-2026 12:27 UTC |
| Biaya aktual per layanan | Portal → Cost Management → Cost analysis (scope Azure for Students) | 09-11-2026 |
| Faktur pertama | Portal → Invoices, faktur G189578384 | periode 22–30 Sep 2026 |
| Saldo kredit dan biaya bulan berjalan | Portal → Education → Overview (gambar `ev07/ev07-kredit-education.png`) | 10-11-2026 22:40 WIB |
| Budget alert | Azure CLI `az consumption budget list` | 10-11-2026 22:40 WIB |
| Tarif bandwidth | https://azure.microsoft.com/pricing/details/bandwidth/ | diakses 10-11-2026 |

Catatan: `az consumption usage list` mengembalikan 41 baris untuk 1–10 Nov 2026, tetapi kolom kategori, meter, dan biaya kosong (`None`) untuk jenis langganan ini, sehingga rincian per layanan diambil dari Cost analysis di portal.

## 2. Tarif bruto (sebelum kredit dan jatah gratis)

| Komponen | Spesifikasi | USD/bulan | USD/12 bulan |
|---|---|---|---|
| Compute VM | 1 × B2ats v2 (2 vCPU, 1 GiB), Linux, 730 jam | 8,69 | 104,28 |
| Managed disk | 1 × P4 (32 GiB Premium SSD LRS) | 5,28 | 63,36 |
| Egress | 5 GB keluar (masuk jatah gratis 100 GB/bulan) | 0,00 | 0,00 |
| **Subtotal VM (kalkulator)** | | **13,9665** | **167,60** |
| Public IPv4 | 1 × Standard Static, 730 jam | 3,65 | 43,80 |
| Blob Storage (backup) | Block Blob GPv2, LRS, Hot, 1 GB + 10.000 operasi per jenis (batas atas) | 0,1388 | 1,67 |
| **Total bruto** | | **17,7553 ≈ 17,76** | **213,06** |
| Kontingensi 10% | | | 21,31 |
| **TCO 12 bulan bruto** | | | **234,37** |

Perhitungan: (13,9665 + 3,65 + 0,1388) × 12 = 213,06 (bukan 17,76 × 12 = 213,12, yang muncul karena pembulatan lebih dahulu).

## 3. Komponen lain dalam cakupan TCO

| Komponen | Biaya | Dasar |
|---|---|---|
| Domain | USD 0 | Subdomain disediakan dosen (belum diterima); sementara memakai DNS name label Azure |
| DNS | USD 0 | DNS name label pada public IP Azure tanpa biaya tambahan |
| Sertifikat TLS | USD 0 | Let's Encrypt lewat Caddy |
| Egress | USD 0 (perkiraan) | 100 GB pertama per bulan gratis; selanjutnya USD 0,12/GB dari Australia. Lalu lintas pilot (puluhan siswa, halaman teks) jauh di bawah 100 GB |
| Layanan pihak ketiga / API | USD 0 | Tidak ada; model cek risiko berjalan di VM |
| Repository dan CI | USD 0 | GitHub akun gratis |
| Tenaga pengembangan dan pemeliharaan | Nonkas, tidak dikonversi ke uang | Proyek akademik; jam kerja dicatat per milestone mulai M05 |
| Biaya kas (uang keluar) | USD 0 | Seluruh tagihan dipotong dari kredit Azure for Students |

## 4. Biaya aktual (bukan estimasi)

### 4.1 Faktur pertama

| Faktur | Periode | Biaya | Kredit | Total dibayar |
|---|---|---|---|---|
| G189578384 | 22–30 Sep 2026 | USD 1,95 | −USD 1,95 | USD 0,00 (Paid) |

### 4.2 Cost analysis 1 Sep – 9 Nov 2026

| Layanan | USD |
|---|---|
| Storage (managed disk) | 7,91 |
| Virtual Network (public IP) | 5,52 |
| Virtual Machines | 0,00 |
| Bandwidth | 0,00 |
| **Total** | **13,43** |

Rincian meter memuat "B2ats v2 – Free": compute VM tidak ditagih selama periode ini karena tercakup jatah gratis langganan. Biaya tetap berasal dari disk dan public IP, yang **tetap ditagih walaupun VM dihentikan (deallocated)**. Prakiraan portal untuk November 2026: USD 8,79.

### 4.3 Bulan berjalan (November 2026)

| Sumber | Biaya 1–10 Nov 2026 |
|---|---|
| Education → Overview, "November costs" | USD 3,08 |
| Budget `budget-cloudlits-bulanan`, `currentSpend` | USD 2,79 |

Selisih kecil antara dua angka berasal dari waktu pembaruan data yang berbeda di Azure. Laju 1–10 Nov (USD 3,08 dalam 10 hari ≈ USD 9,2/bulan) sejalan dengan perkiraan biaya nyata pada bagian 6.

## 5. Kredit Azure for Students

Dari Portal → Education → Overview (gambar `ev07/ev07-kredit-education.png`, email disamarkan):

| Parameter | 09-11-2026 | 10-11-2026 |
|---|---|---|
| Kredit tersedia | USD 87 dari USD 100 | **USD 86 dari USD 100** |
| Hari sampai kredit berakhir | 317 | **316** |
| Tanggal berakhir | 22-09-2027 | **22-09-2027** |
| Biaya bulan berjalan | — | USD 3,08 (November) |

Catatan: halaman Azure Sponsorships menampilkan "This account does not have an active Sponsorship" untuk akun ini, sehingga sumber saldo yang dipakai adalah Education Hub.

**Kredit bukan VM gratis permanen.** Kredit USD 100 habis bila terpakai atau pada 22-09-2027, mana yang lebih dulu. Jatah compute gratis (meter "B2ats v2 – Free") adalah manfaat langganan yang dapat berakhir; bila berakhir, compute ditagih penuh.

## 6. Burn-rate dan perkiraan kredit habis

| Skenario | Biaya/bulan | Kredit USD 86 cukup untuk | Perkiraan habis | Sebelum 22-09-2027? |
|---|---|---|---|---|
| A. Kondisi sekarang: compute gratis, disk + IP + Blob ditagih | USD 9,07 (5,28 + 3,65 + 0,14) | ≈ 9,5 bulan | sekitar akhir Agustus 2027 | Ya, sedikit lebih awal |
| B. Jatah compute gratis berakhir, VM menyala terus | USD 17,76 | ≈ 4,8 bulan | sekitar awal April 2027 | Ya, jauh lebih awal |
| C. Semua resource dihapus | USD 0 | — | — | — |

Perhitungan: 86 ÷ 9,07 = 9,48 bulan dari 10-11-2026; 86 ÷ 17,76 = 4,84 bulan dari 10-11-2026. Ini angka turunan, bukan tagihan.

**Menghentikan VM tidak menghentikan biaya**: disk P4 dan public IP Static tetap ditagih (sekitar USD 8,93/bulan). Biaya hanya berhenti bila resource dihapus.

## 7. Budget alert

```bash
az consumption budget list --query "[].{name:name,amount:amount,timeGrain:timeGrain,start:timePeriod.startDate,end:timePeriod.endDate,currentSpend:currentSpend.amount,alerts:notifications.*.{enabled:enabled,operator:operator,threshold:threshold,type:thresholdType}}" -o json
```

```json
[
  {
    "alerts": [
      { "enabled": true, "operator": "GreaterThan", "threshold": "50.0",  "type": null },
      { "enabled": true, "operator": "GreaterThan", "threshold": "80.0",  "type": null },
      { "enabled": true, "operator": "GreaterThan", "threshold": "100.0", "type": null },
      { "enabled": true, "operator": "GreaterThan", "threshold": "100.0", "type": null }
    ],
    "amount": "10.0",
    "currentSpend": "2.7873432830000002",
    "end": "2027-09-22T00:00:00Z",
    "name": "budget-cloudlits-bulanan",
    "start": "2026-11-01T00:00:00Z",
    "timeGrain": "Monthly"
  }
]
```

| Parameter | Nilai |
|---|---|
| Nama | `budget-cloudlits-bulanan` |
| Batas | USD 10 per bulan, reset bulanan |
| Masa berlaku | 01-11-2026 s.d. 22-09-2027 (sama dengan masa kredit) |
| Alert | 4 aktif: 50% (USD 5), 80% (USD 8), 100% (USD 10), 100% (USD 10). Menurut detail budget di portal (09-11-2026): tiga berjenis *Actual* dan satu *Forecasted*; CLI tidak menampilkan jenisnya (`type: null`) |
| Penerima | Email mahasiswa (disamarkan) |
| Batasan | Budget hanya mengirim notifikasi; tidak menghentikan VM atau resource. Penghentian dilakukan manual |

Batas USD 10 dipilih karena sedikit di atas biaya nyata skenario A (USD 9,07): alert 100% menandakan ada biaya di luar kebiasaan (misalnya compute mulai ditagih).

## 8. Keputusan setelah kredit habis

| Opsi | Biaya | Keputusan |
|---|---|---|
| **A. Hentikan proyek: simpan backup final di luar Azure, lalu hapus resource group** | USD 0 setelah dihapus | **Dipilih** |
| B. Upgrade ke Pay-as-you-go | USD 9,07–17,76/bulan dari dana pribadi | Tidak dipilih (tidak ada pendanaan) |
| C. Kurangi biaya tetap (mis. IP dinamis, hapus IP saat tidak dipakai) | Hemat sekitar USD 3,65/bulan | Tidak dipilih saat ini; butuh perubahan arsitektur DNS dan pengujian ulang |

Pemicu penghentian (usulan, menunggu konfirmasi dosen): **sisa kredit di Education Hub < USD 15**, atau **praktikum selesai** (akhir Semester Ganjil 2026/2027, pertemuan 16/UAS), mana yang lebih dulu.

Pemantauan: saldo kredit dibaca setiap 2 minggu di Education → Overview dan dicatat dengan tanggal (09-11-2026: USD 87; 10-11-2026: USD 86; berikutnya sekitar 23-11-2026).

## 9. Inventaris resource yang ditagih

Resource group `AmeliaOkta_` (Australia East), 09-11-2026: VM `VpsAmel`, OS disk P4, public IP `VpsAmel-ip`, network interface, NSG, virtual network, SSH key, dan storage account `cloudlitsbackupamel`. Resource group historis `cc-p2-…` (biaya USD 0,01 pada Cost analysis) sudah tidak ada.

## 10. Hasil

| Kriteria | Expected | Actual | Status |
|---|---|---|---|
| Saldo dan masa berlaku kredit | Tercatat dengan sumber dan tanggal | USD 86 dari 100, berakhir 22-09-2027 (Education, 10-11-2026) | LULUS |
| Burn-rate VM + disk + IP | Dihitung dari tarif dan biaya aktual | Nyata USD 9,07/bulan; bruto USD 17,76/bulan; Cost analysis 13,43 (1 Sep–9 Nov) | LULUS |
| Masa aktif sesuai kredit | Perkiraan kapan kredit habis | Skenario A ≈ akhir Agustus 2027; skenario B ≈ awal April 2027 | LULUS |
| Budget alert | Aktif dan terdokumentasi | USD 10/bulan, 4 alert aktif (CLI 10-11-2026) | LULUS |
| Keputusan stop/upgrade | Tertulis dengan pemicu | Opsi A, pemicu < USD 15 atau akhir praktikum | LULUS (konfirmasi dosen menunggu) |
| Sumber tarif bertanggal | Region, tanggal, mata uang | Kalkulator 09-11-2026, Australia East, USD | LULUS |

## 11. Isu tersisa

1. **Tarif kalkulator tetap estimasi** dan dapat berubah; dicek ulang tiap milestone.
2. **Rincian biaya per layanan tidak tersedia lewat CLI** untuk langganan ini; bukti rincian bergantung pada portal Cost analysis.
3. **Jatah compute gratis selama 12 bulan adalah asumsi**; baru terbukti untuk 1 Sep–9 Nov 2026. Bila berakhir lebih awal, berlaku skenario B.
4. **Faktur Oktober 2026** belum dilampirkan.
5. **Pemicu penghentian** menunggu konfirmasi dosen.
6. Berkas ekspor `azure-pricing-estimate-2026-11-09.xlsx` disimpan di luar repository; dapat diperiksa dosen bila diminta.
