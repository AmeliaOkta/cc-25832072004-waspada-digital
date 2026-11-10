# EV-09: Uji Domain — Instrumen Asesmen, Evaluasi Pembelajaran, Privasi Kuis, dan Matriks Uji (Temuan 06)

| Item | Isi |
|---|---|
| Proyek | CloudLits — CC-PTI2802-25832072004-CLOUDLITS |
| Mahasiswa | Amelia Okta Ramadani (25832072004) |
| Temuan dosen | 06: konten literasi digital dan evaluasi pengguna memerlukan standar akurasi serta penggunaan data siswa (baris 61) |
| Revisi | 06 (draf awal, commit 2dcf01f), diperbarui 06b (10-11-2026) |
| Status | **Sebagian.** Instrumen 10 butir, rubrik, desain pre/post-test, desain privasi kuis, dan matriks uji **sudah dirancang**. **Belum dilaksanakan:** telaah guru/ahli, pre/post-test, dan pengujian sistem (fitur kuis dan cek risiko belum diimplementasikan; dijadwalkan M05–M11) |

> Sesuai arahan dosen ("rencana implementasi tidak boleh dilaporkan seolah-olah pengujian sudah selesai"), seluruh uji pada bagian 6 berstatus **BELUM DIJALANKAN** sampai ada log hasil yang dapat diperiksa. Draf 2dcf01f menandai DOM-01 sampai DOM-06 sebagai "LULUS" dan instrumen sebagai "Disetujui"; status itu **dicabut** pada revisi ini karena belum ada aplikasi kuis, log uji, maupun lembar telaah yang ditandatangani.

## 1. Tujuan dan kriteria dari arahan dosen

| Sumber arahan | Yang diminta | Bagian di berkas ini |
|---|---|---|
| Temuan 06 | Rubrik materi, penilaian efektif, akses peserta, data anonim, evaluasi hasil belajar | 2, 3, 4, 5 |
| Temuan 06 — kriteria uji | Pre/post-test anonim dan audit akurasi konten bersama ahli | 4, 7 |
| Temuan 06 — bukti minimum | Matriks tes positif/negatif, data sintetis, log, status lulus/gagal | 6 |
| III.1 | ≥ 10 butir sesuai tujuan; uji terbatas sukarela dan anonim; jumlah, cara memilih responden, perubahan skor per butir, potensi bias; validasi isi guru/ahli; tanpa klaim kausal | 2, 4, 7 |
| III.2 | Tanpa nama/telepon/alamat/pengenal siswa; pemisahan hak akses admin/peserta; batas retensi; proses penghapusan; peserta tidak dapat membaca hasil peserta lain; ekspor tanpa identitas | 5, 6 |

## 2. Instrumen asesmen literasi digital (10 butir)

- Sasaran: siswa kelas X. Waktu pengerjaan: 10–15 menit.
- Data peserta: hanya **kode acak** yang dibuat sistem dan **kode kelas**; tanpa nama, NIS/NISN, nomor HP, atau email.
- Status: **draf, belum ditelaah guru/ahli** (bagian 7).

### Soal 01 — Phishing kuota belajar

Sebuah pesan WhatsApp berantai berbunyi: *"KEMENDIKDASMEN BAGIKAN KUOTA GRATIS 50GB UNTUK SISWA DAN GURU DALAM RANGKA HARI GURU NASIONAL! Klaim kuota Anda segera di tautan: http://kuota-gratis-kemendikdasmen.xyz-promo.site/klaim sebelum kuota habis hari ini!"*

Tindakan apa yang paling tepat dan aman dilakukan oleh siswa?

- A. Mengklik tautan dan memasukkan nomor HP serta kode OTP yang masuk lewat SMS.
- B. Meneruskan pesan tersebut ke grup kelas agar teman-teman tidak ketinggalan kuota.
- C. Mengabaikan tautan, tidak menyebarkan pesan, serta memeriksa informasi di situs resmi kementerian (kemendikdasmen.go.id).
- D. Mengisi formulir nama lengkap dan nomor WhatsApp karena tautan memuat nama kementerian.

**Kunci:** C. **Indikator:** mengenali bahwa domain utama tautan adalah `xyz-promo.site` (bukan `.go.id`), sehingga nama kementerian di depannya hanya kamuflase; tidak memberikan OTP.

### Soal 02 — Social engineering hadiah TikTok

Kamu menerima direct message (DM) TikTok dari akun yang memakai logo TikTok resmi: *"Selamat! Akun Anda terpilih memenangkan saldo e-wallet Rp2.000.000. Untuk aktivasi hadiah, kirimkan tangkapan layar kode verifikasi 6 angka yang baru saja dikirim ke SMS kamu."*

Mengapa kode 6 angka tersebut TIDAK BOLEH diberikan kepada pengirim?

- A. Karena kode 6 angka tersebut adalah One-Time Password (OTP) untuk login/mengambil alih akun pengguna.
- B. Karena saldo e-wallet baru bisa masuk jika jumlah digitnya 8 angka.
- C. Karena pengirim pesan belum mem-follow akun TikTok kita.
- D. Karena pengiriman hadiah TikTok hanya bisa lewat transfer rekening bank fisik.

**Kunci:** A. **Indikator:** memahami OTP sebagai rahasia pribadi yang menjadi sasaran pengambilalihan akun.

### Soal 03 — Tautan singkat

Di grup obrolan, seseorang membagikan tautan singkat `bit.ly/beasiswa-laptop-2026` dengan janji pembagian laptop gratis bagi siswa berprestasi. Langkah pencegahan pertama sebelum memutuskan membuka tautan adalah:

- A. Langsung mengklik tautan karena bit.ly adalah penyedia layanan resmi pemerintah.
- B. Memeriksa tujuan asli tautan dengan layanan pemeriksa/pembuka tautan singkat (URL expander) tanpa membukanya langsung.
- C. Membuka tautan menggunakan mode penyamaran (Incognito) agar virus tidak masuk ke ponsel.
- D. Membagikan tautan ke grup lain sambil bertanya apakah ada yang sudah mencoba.

**Kunci:** B. **Indikator:** memahami bahwa tautan singkat menyembunyikan alamat asli dan cara memeriksanya tanpa membuka.

### Soal 04 — Video sensasional

Sebuah video viral di TikTok menampilkan narasi: *"Mulai besok seluruh sekolah di Jawa Barat libur total 1 bulan akibat cuaca ekstrem mendadak!"* Video diiringi musik dramatis dan potongan klip berita lama tanpa tanggal liputan. Sikap kritis yang wajib dilakukan adalah:

- A. Langsung membagikan video ke grup keluarga agar semua orang bersiap-siap.
- B. Mempercayai video karena sudah disukai lebih dari 100.000 pengguna.
- C. Memeriksa portal berita kredibel atau pengumuman resmi Dinas Pendidikan.
- D. Berkomentar di video menanyakan apakah guru juga ikut libur.

**Kunci:** C. **Indikator:** tidak memakai jumlah suka/tayang sebagai ukuran kebenaran; mencari sumber resmi.

### Soal 05 — Oversharing data pribadi

Setelah menerima kartu pelajar atau sertifikat lomba, tindakan manakah yang mencerminkan kesadaran privasi yang baik saat ingin mengunggah ke Instagram Story?

- A. Mengunggah foto kartu pelajar secara utuh agar terlihat jelas nama sekolah dan jurusannya.
- B. Menutup (blur) informasi sensitif seperti NISN, tanggal lahir, alamat rumah, dan kode batang/QR sebelum diunggah.
- C. Mengunggah sertifikat dan menambahkan lokasi terkini (live location) rumah.
- D. Membagikan tangkapan layar kartu ujian yang mencantumkan username dan kata sandi ujian.

**Kunci:** B. **Indikator:** mempraktikkan minimalisasi data pribadi di ruang publik.

### Soal 06 — Domain tiruan

Perhatikan alamat web berikut: `https://www.banksejahtera.co.id.klik-layanan-edukasi.com/login`. Mengapa alamat ini patut dicurigai sebagai situs berbahaya meskipun diawali `https://`?

- A. Karena protokol `https://` sudah tidak aman lagi digunakan di perbankan modern.
- B. Karena domain utamanya adalah `klik-layanan-edukasi.com`; tulisan `banksejahtera.co.id` di depannya hanya subdomain tiruan untuk mengecoh.
- C. Karena ekstensi `.com` hanya boleh digunakan untuk situs toko online.
- D. Karena situs perbankan tidak diperbolehkan memiliki kata 'login' pada URL.

**Kunci:** B. **Indikator:** membaca domain utama dari kanan; memahami bahwa gembok HTTPS tidak menjamin pemilik situs. ("Bank Sejahtera" adalah nama fiktif.)

### Soal 07 — Malware APK

Seorang teman mengirim berkas lewat WhatsApp bernama `Foto_Kegiatan_Kemah.apk` dan meminta kamu segera memasangnya untuk melihat dokumentasi foto. Apa yang harus kamu lakukan?

- A. Segera memasang aplikasi tersebut karena nama filenya memuat kata 'Foto'.
- B. Tidak memasang berkas, menghapusnya, dan memberi tahu teman bahwa `.apk` adalah paket aplikasi Android yang berpotensi memuat malware pencuri data/SMS.
- C. Mengganti ekstensi `.apk` menjadi `.jpg` agar bisa dibuka di galeri.
- D. Mengirim berkas ke grup sekolah untuk bertanya apakah foto mereka ada di dalamnya.

**Kunci:** B. **Indikator:** mengenali aplikasi jahat yang menyamar sebagai foto/dokumen.

### Soal 08 — Hoaks kesehatan

Keluarga kamu menerima pesan di grup WhatsApp yang mengklaim bahwa air rebusan daun tertentu dapat menyembuhkan penyakit berat dalam 24 jam tanpa resep dokter. Cara terbaik untuk membantu mengecek klaim tersebut adalah:

- A. Memeriksa klaim melalui situs cek fakta independen (misalnya turnbackhoax.id, cekfakta.com) atau situs resmi Kementerian Kesehatan.
- B. Mengabaikan saja dan membiarkan anggota keluarga mencoba resep tersebut.
- C. Membalas dengan marah di grup dan menuduh pengirim menyebarkan kebohongan.
- D. Mencari video testimoni di TikTok yang mendukung klaim tersebut.

**Kunci:** A. **Indikator:** memanfaatkan platform cek fakta dan sumber kesehatan resmi.

### Soal 09 — Kata sandi

Manakah praktik pengelolaan kata sandi yang paling aman untuk akun belajar dan media sosial siswa?

- A. Menggunakan tanggal lahir sendiri agar mudah diingat di semua akun.
- B. Menggunakan kata sandi yang sama untuk email sekolah, akun game, dan media sosial.
- C. Menggunakan frasa sandi yang panjang dan unik, berbeda untuk tiap akun, serta mengaktifkan verifikasi dua langkah (2FA).
- D. Menuliskan kata sandi pada bio profil media sosial yang disetel privat.

**Kunci:** C. **Indikator:** memahami kata sandi kuat, tidak dipakai ulang, dan 2FA.

### Soal 10 — Jejak digital

Pernyataan manakah yang paling akurat mengenai jejak digital?

- A. Komentar dan postingan langsung terhapus permanen begitu tombol 'hapus' ditekan.
- B. Data yang pernah diunggah dapat disimpan kembali oleh pihak lain (tangkapan layar, arsip web) dan dapat memengaruhi reputasi di masa depan.
- C. Mode penyamaran (Incognito) menjamin penyedia internet dan situs web tidak dapat mencatat aktivitas kita.
- D. Hanya tokoh publik dan pejabat yang memiliki jejak digital penting.

**Kunci:** B. **Indikator:** menyadari bahwa jejak digital sulit dihapus dan perlu kehati-hatian dalam berbagi.

### 2.1 Ringkasan kunci dan perubahan dari draf 2dcf01f

| Butir | Kunci | Dimensi | Perubahan revisi 06b |
|---|---|---|---|
| 01 | C | Keamanan & kredensial | Nama dan domain kementerian disesuaikan menjadi Kemendikdasmen (`kemendikdasmen.go.id`); indikator dikoreksi: domain utama `xyz-promo.site`, bukan "TLD .xyz" |
| 02 | A | Keamanan & kredensial | — |
| 03 | B | Verifikasi & sumber | Opsi D diganti karena draf (minta verifikasi ke pembina) juga dapat dianggap benar |
| 04 | C | Verifikasi & sumber | — |
| 05 | B | Privasi & jejak digital | — |
| 06 | B | Verifikasi & sumber | Nama bank nyata diganti nama fiktif agar tidak memakai merek nyata dalam contoh penipuan |
| 07 | B | Keamanan & kredensial | — |
| 08 | A | Verifikasi & sumber | — |
| 09 | C | Keamanan & kredensial | Redaksi kunci dirapikan (frasa sandi panjang dan unik) |
| 10 | B | Privasi & jejak digital | Opsi B dirapikan |

## 3. Rubrik penskoran

| Komponen | Ketentuan |
|---|---|
| Skor per butir | Benar 10, salah atau kosong 0 |
| Skor total | 0–100 |
| Keamanan informasi & kredensial | Butir 01, 02, 07, 09 (40 poin) |
| Verifikasi hoaks & evaluasi sumber | Butir 03, 04, 06, 08 (40 poin) |
| Privasi & jejak digital | Butir 05, 10 (20 poin) |

| Skor | Kategori | Makna |
|---|---|---|
| 80–100 | Mahir | Konsisten memeriksa sumber dan struktur tautan sebelum bertindak |
| 60–70 | Cukup | Memahami bahaya dasar, masih rentan pada teknik yang halus (domain tiruan, APK) |
| < 60 | Perlu bimbingan | Belum terbiasa memeriksa sumber; berisiko membocorkan kredensial |

Kategori adalah usulan dan **ditetapkan setelah telaah guru** (bagian 7).

## 4. Desain evaluasi pre-test dan post-test

| Aspek | Rancangan |
|---|---|
| Responden | 20–30 siswa satu kelas X yang diizinkan guru; **sukarela**; siswa yang tidak ikut tidak dirugikan |
| Cara memilih | *Convenience sampling* (kelas yang diizinkan); jumlah undangan, peserta, dan yang tidak menyelesaikan dicatat |
| Izin | Izin sekolah/guru dan persetujuan orang tua/wali sebelum skor disimpan (laporan 8.2); tanpa persetujuan, siswa boleh mengerjakan tanpa skor disimpan |
| Identitas | Kode acak dibuat sistem (mis. `K7Q2`) + kode kelas; kode tidak dapat ditelusuri ke nama |
| Alur | Pre-test 10 butir → satu modul materi CloudLits (15–20 menit) → post-test 10 butir yang sama dengan urutan butir dan opsi diacak |
| Pre-test murni | Pre-test dikerjakan **sebelum** materi apa pun (memperbaiki kelemahan riset 07-11-2026, ev03) |
| Analisis | Rata-rata dan median skor pre vs post; **persentase benar per butir** pre vs post; jumlah peserta dengan skor naik/tetap/turun |
| Target | Rata-rata post-test lebih tinggi daripada pre-test (laporan 2.2); kenaikan 10–15 poin dipakai sebagai acuan indikatif (laporan 10.4), bukan syarat kelulusan |
| Potensi bias | Efek pengulangan soal yang sama; tanpa kelompok kontrol; efek kebaruan aplikasi; kehadiran peneliti/guru; sampel kecil dan tidak acak |
| Batas kesimpulan | Hasil hanya menggambarkan kelompok uji; **tidak** dipakai untuk klaim efektivitas kausal |
| Pelaporan | Rekap anonim per kode dan per butir di `ev09/hasil-pre-post.csv` (setelah pelaksanaan) |

## 5. Desain privasi data kuis

### 5.1 Data yang disimpan

| Data | Disimpan | Keterangan |
|---|---|---|
| Nama, NIS/NISN, nomor HP, email, alamat, foto | **Tidak** | Tidak ada kolom untuk data ini |
| Kode peserta acak | Ya | Dibuat sistem; tidak memuat nama |
| Kode kelas | Ya | Untuk agregat per kelas |
| Jenis percobaan (pre/post), jawaban per butir, skor, waktu mulai/selesai | Ya | Untuk umpan balik dan analisis butir |
| Alamat IP pengunjung | Tidak disimpan di database | Log akses server dibatasi; diperiksa sebelum pilot |

### 5.2 Hak akses per peran

| Peran | Boleh | Tidak boleh |
|---|---|---|
| Peserta | Mengerjakan kuis; melihat skor **sendiri** pada sesinya | Melihat hasil peserta lain; mengubah soal |
| Guru | Melihat **agregat** per kode kelas (rata-rata, % benar per butir) | Melihat jawaban per peserta |
| Admin (pengelola) | Mengelola soal; ekspor anonim; menghapus data | — (tindakan admin dicatat di log) |

### 5.3 Retensi dan penghapusan

| Aspek | Ketentuan |
|---|---|
| Retensi | Data kuis dihapus **30 hari setelah UAS** (sejalan NFR-02 dan laporan 8.2) |
| Penghapusan | Admin menjalankan prosedur hapus per kode kelas; hasilnya dicatat (jumlah baris terhapus, tanggal) |
| Backup | Salinan di Azure Blob ikut terhapus otomatis paling lambat **14 hari** setelah penghapusan, karena retensi backup 14 hari (ev05) |
| Ekspor | Hanya kode acak, kode kelas, jawaban, skor; tanpa kolom identitas |

## 6. Matriks uji domain (positif dan negatif)

Semua uji dijalankan pada **data sintetis** (kode peserta buatan, bukan siswa nyata). Status diisi dari log nyata saat dijalankan.

| ID | Skenario | Jenis | Data uji (sintetis) | Hasil yang diharapkan | Milestone | Status |
|---|---|---|---|---|---|---|
| DOM-01 | Skor kuis dihitung benar | Positif | 10 jawaban sesuai kunci | Skor 100; tersimpan di SQLite | M05 | BELUM DIJALANKAN |
| DOM-02 | Skor sebagian | Positif | 6 benar, 4 salah | Skor 60 | M05 | BELUM DIJALANKAN |
| DOM-03 | Jawaban kosong atau terpotong | Negatif | Formulir tanpa jawaban | HTTP 400 dengan pesan jelas; tanpa stack trace; tidak tersimpan | M05 | BELUM DIJALANKAN |
| DOM-04 | Data identitas tidak tersimpan | Privasi | Kiriman berisi field tambahan `nama=Budi` | Field diabaikan; tabel tidak memiliki kolom identitas | M05 | BELUM DIJALANKAN |
| DOM-05 | Peserta membuka hasil peserta lain (IDOR) | Negatif / privasi | Sesi peserta A meminta hasil milik kode B | HTTP 403/404; data B tidak tampil | M05 | BELUM DIJALANKAN |
| DOM-06 | Guru hanya melihat agregat | Privasi | Akun guru membuka rekap kelas `X-UJI` | Tampil rata-rata dan % benar per butir, tanpa jawaban per peserta | M05+ | BELUM DIJALANKAN |
| DOM-07 | Operasi tulis soal tanpa otorisasi | Negatif | Permintaan ubah soal tanpa login admin | HTTP 401/403 (FR-04) | M05+ | BELUM DIJALANKAN |
| DOM-08 | Injeksi SQL/XSS pada kode kelas | Keamanan | `' OR 1=1 --`, `<script>alert(1)</script>` | Disimpan sebagai teks biasa atau ditolak; tidak dieksekusi | M10 | BELUM DIJALANKAN |
| DOM-09 | Ekspor anonim | Privasi | Ekspor CSV kelas `X-UJI` | Hanya kode acak, kode kelas, jawaban, skor | M05+ | BELUM DIJALANKAN |
| DOM-10 | Penghapusan sesuai retensi | Privasi | Hapus kelas `X-UJI` | Baris terhapus; jumlah tercatat; tidak muncul lagi | M05+ | BELUM DIJALANKAN |
| DOM-11 | Cek risiko: tautan resmi | Positif (FR-06) | `https://kemendikdasmen.go.id/` | Label risiko rendah dengan alasan | M11 | BELUM DIJALANKAN |
| DOM-12 | Cek risiko: tautan phishing | Negatif (FR-06) | `http://kuota-gratis-kemendikdasmen.xyz-promo.site/` | Label risiko tinggi; alasan: domain utama bukan `.go.id`, nama lembaga di subdomain | M11 | BELUM DIJALANKAN |
| DOM-13 | Cek risiko: berkas APK | Negatif (FR-06) | Teks `Unduh Foto_Kemah.apk` | Label peringatan berkas aplikasi | M11 | BELUM DIJALANKAN |
| DOM-14 | Input cek risiko tidak disimpan | Privasi (FR-06) | Kirim teks uji, lalu periksa database dan log | Isi teks tidak ada di database maupun log | M11 | BELUM DIJALANKAN |

Format log saat dijalankan: tanggal/waktu, commit aplikasi, perintah atau langkah, keluaran (kode HTTP, isi respons ringkas), status LULUS/GAGAL, dan catatan.

## 7. Telaah isi oleh guru/ahli

| Aspek | Isi |
|---|---|
| Penelaah | [ISI: inisial, jabatan (mis. guru Informatika), institusi; disamarkan bila perlu] |
| Tanggal telaah | [ISI] |
| Status | **Belum ditelaah** |
| Bukti | Lembar telaah bertanda tangan atau pesan persetujuan, disimpan di luar repository; ringkasan dicatat di tabel di bawah |

Lembar telaah per butir (diisi penelaah):

| Butir | Sesuai tujuan materi (Y/T) | Kunci benar dan tunggal (Y/T) | Bahasa sesuai kelas X (Y/T) | Saran perbaikan |
|---|---|---|---|---|
| 01 | | | | |
| 02 | | | | |
| 03 | | | | |
| 04 | | | | |
| 05 | | | | |
| 06 | | | | |
| 07 | | | | |
| 08 | | | | |
| 09 | | | | |
| 10 | | | | |

Keputusan penelaah: [ ] layak dipakai  [ ] layak dengan perbaikan  [ ] perlu revisi besar

## 8. Status per kriteria

| Kriteria | Status 10-11-2026 |
|---|---|
| ≥ 10 butir asesmen dengan kunci dan indikator | **Ada** (bagian 2) |
| Rubrik penskoran | **Ada** (bagian 3), menunggu telaah |
| Desain pre/post-test anonim, sampling, bias, batas kesimpulan | **Ada** (bagian 4) |
| Desain privasi: data, peran, retensi, penghapusan, ekspor | **Ada** (bagian 5) |
| Matriks uji positif/negatif dengan data sintetis | **Ada** (bagian 6), **belum dijalankan** |
| Telaah isi oleh guru/ahli | **Belum** |
| Pelaksanaan pre/post-test dan rekap per butir | **Belum** (setelah fitur kuis M05 dan izin) |
| Log uji sistem | **Belum** |
