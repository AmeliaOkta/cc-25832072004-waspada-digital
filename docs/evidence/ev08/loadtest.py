"""Uji beban sederhana CloudLits (tanpa pustaka tambahan).

Pemakaian (PowerShell di laptop):
    python loadtest.py

Mengirim permintaan HTTPS dari N pengguna bersamaan selama D detik ke beberapa
halaman, lalu mencatat latensi (p50/p95/p99/maks), jumlah status HTTP, dan
error rate. Hasil mentah disimpan ke CSV.
"""
import csv
import ssl
import statistics
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = "https://cloudlits-amelia.australiaeast.cloudapp.azure.com"
PATHS = ["/", "/", "/api/info", "/health"]   # "/" = halaman materi (4 studi kasus), diberi bobot 50%
USERS = 5                          # pengguna bersamaan (NFR-04)
DURATION = 60                      # detik pengukuran
WARMUP = 5                         # detik pemanasan (tidak dihitung)
TIMEOUT = 15

ctx = ssl.create_default_context()  # sertifikat TLS diverifikasi (tanpa -k)
results = []                         # (waktu_mulai, path, status, latensi_ms, galat)
lock = threading.Lock()


def worker(stop_at, record_from):
    i = 0
    while time.time() < stop_at:
        path = PATHS[i % len(PATHS)]
        i += 1
        t0 = time.time()
        status, err = 0, ""
        try:
            req = urllib.request.Request(BASE + path, headers={"User-Agent": "cloudlits-loadtest"})
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
                r.read()
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:  # timeout, koneksi gagal
            err = type(e).__name__
        ms = (time.time() - t0) * 1000
        if t0 >= record_from:
            with lock:
                results.append((t0, path, status, ms, err))


def pct(values, p):
    if not values:
        return float("nan")
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round(p / 100 * len(s) + 0.5)) - 1))
    return s[k]


def main():
    start = time.time()
    record_from = start + WARMUP
    stop_at = record_from + DURATION
    print(f"Mulai  : {datetime.now(timezone.utc).isoformat(timespec='seconds')} (UTC)")
    print(f"Target : {BASE}  halaman {PATHS}")
    print(f"Beban  : {USERS} pengguna bersamaan, {DURATION} s (+{WARMUP} s pemanasan)\n")
    threads = [threading.Thread(target=worker, args=(stop_at, record_from)) for _ in range(USERS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    end = datetime.now(timezone.utc).isoformat(timespec='seconds')

    def summary(label, rows):
        lat = [r[3] for r in rows]
        ok = [r for r in rows if 200 <= r[2] < 400]
        e5 = [r for r in rows if r[2] >= 500]
        fail = [r for r in rows if r[2] == 0]
        n = len(rows)
        print(f"[{label}] permintaan={n}  rps={n / DURATION:.2f}  sukses={len(ok)}  "
              f"5xx={len(e5)}  gagal_koneksi={len(fail)}  error_rate={(len(e5) + len(fail)) / n * 100 if n else 0:.2f}%")
        print(f"         p50={pct(lat, 50):.0f} ms  p95={pct(lat, 95):.0f} ms  p99={pct(lat, 99):.0f} ms  "
              f"maks={max(lat) if lat else 0:.0f} ms  rata2={statistics.mean(lat) if lat else 0:.0f} ms")

    print(f"Selesai: {end} (UTC)\n")
    summary("SEMUA", results)
    for p in dict.fromkeys(PATHS):
        summary(p, [r for r in results if r[1] == p])
    codes = {}
    for r in results:
        codes[r[2]] = codes.get(r[2], 0) + 1
    print("\nStatus HTTP:", dict(sorted(codes.items())))
    errs = {r[4] for r in results if r[4]}
    if errs:
        print("Jenis galat:", errs)

    fname = f"loadtest-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    with open(fname, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["waktu_utc", "path", "status", "latensi_ms", "galat"])
        for t0, path, status, ms, err in results:
            w.writerow([datetime.fromtimestamp(t0, timezone.utc).isoformat(timespec='milliseconds'), path, status, f"{ms:.1f}", err])
    print(f"\nData mentah: {fname}")


if __name__ == "__main__":
    main()
