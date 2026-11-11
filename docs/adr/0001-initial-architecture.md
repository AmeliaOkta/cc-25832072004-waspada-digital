# ADR-0001: Initial VPS Deployment Architecture

## Status

Accepted (M03). Sebagian keputusan diperbarui oleh ADR-0002 dan ADR-0003 (lihat bagian "Pembaruan").

## Context

Azure VM Standard B2ats v2 (2 vCPU, 1 GiB RAM, 30 GiB disk), Ubuntu 24.04.
Aplikasi latihan literasi digital (Waspada Digital) perlu dapat diakses publik lewat IP.

## Decision

* Flask dengan Gunicorn (1 worker, 2 thread), bind 127.0.0.1:8000
* systemd untuk manajemen proses
* Caddy sebagai reverse proxy di port 80
* UFW dan Azure NSG sebagai firewall
* Konten studi kasus disimpan di cases.json di repository

## Alternatives

1. Node.js dengan PM2
2. NGINX dengan Gunicorn
3. Docker
4. SQLite/PostgreSQL untuk konten (ditolak: di luar scope M03)

## Rationale

Stack ringan sesuai RAM 1 GiB, Python 3.12 bawaan Ubuntu 24.04, Caddy sederhana dan siap HTTPS otomatis pada M04. Konten JSON bisa di-review lewat Git dan belum butuh database.

## Consequences

### Positive

* Footprint kecil, mudah direproduksi dan dijelaskan
* Backend tidak terbuka ke internet

### Negative

* Update konten lewat commit, bukan antarmuka admin
* Satu VM berarti tidak ada redundansi

## Review Trigger

Review pada M05 (database) dan M06 (container).

## Pembaruan

| Tanggal | Perubahan | Rujukan |
|---|---|---|
| 08-11-2026 | Akses publik lewat IP dan Caddy port 80 diganti FQDN Azure dengan HTTPS (Let's Encrypt), port 443 dibuka, HTTP dialihkan ke HTTPS | ADR-0002 |
| 09-11-2026 | Database SQLite sintetis disiapkan dan dibackup ke Azure Blob privat; aplikasi masih memakai cases.json | ADR-0003 |
| 10-11-2026 | Satuan disk dikoreksi dari "30 GB" menjadi "30 GiB" (Temuan 07) | ev-penunjang.md |
