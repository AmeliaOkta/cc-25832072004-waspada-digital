# EV-01 — Identitas Sumber Daya dan Spesifikasi VPS

| Item | Isi |
|---|---|
| Proyek | CloudLits — CC-PTI2802-25832072004-CLOUDLITS |
| Mahasiswa | Amelia Okta Ramadani (25832072004) |
| Acuan arahan | Bagian IV.1 (inventaris VPS) dan paket penyerahan "ev01-vps-spec.md (identitas sumber daya + portal)" |
| Waktu pengamatan | 10-11-2026, 22:26 WIB |
| Metode | Azure CLI di Azure Cloud Shell (sisi provider) dan `az vm run-command invoke` (dari dalam VM, dijalankan sebagai root lewat agen VM) |
| Status | Spesifikasi terverifikasi. Isu tersisa pada bagian 7 |

> Berkas ini tidak memuat password, private key, access key, token, Subscription ID, atau data siswa.
> IPv4 publik dicantumkan sebagai identitas infrastruktur sesuai instruksi dosen.

## 1. Ringkasan identitas

| Parameter | Nilai | Sumber |
|---|---|---|
| Provider | Microsoft Azure (langganan Azure for Students) | Portal |
| Resource group | `AmeliaOkta_` | CLI |
| Nama VM (resource) | `VpsAmel` | `az vm show` |
| Hostname di OS | `cc-m03-25832072004` | `hostname` |
| SKU | `Standard_B2ats_v2` (seri Basv2, burstable) | `az vm show` |
| Region | Australia East (`australiaeast`) | `az vm show` |
| Image | Canonical `ubuntu-24_04-lts` / `server` | `az vm show` |
| OS | Ubuntu 24.04.5 LTS, kernel `7.0.0-1017-azure` | `/etc/os-release`, `uname -r` |
| vCPU | 2 (`nproc`); AMD EPYC 7763; 1 socket, 2 thread per core | `nproc`, `lscpu` |
| RAM | 887 MiB terbaca OS (SKU: 1 GiB) + swap 1,0 GiB | `free -h` |
| OS disk | 30 GiB (`sda 30G`), Premium SSD LRS, tier P4, 25 MB/s, create option `FromImage` | `lsblk`, `az disk list` |
| Partisi root | 29 GiB, terpakai 4,0 GiB (14%), sisa 25 GiB | `df -h /` |
| Public IPv4 | `20.58.180.44` — Static, SKU Standard, tier Regional | `az network public-ip show` |
| IPv6 publik | Tidak ada | Portal (08-11-2026) |
| FQDN | `cloudlits-amelia.australiaeast.cloudapp.azure.com` (DNS name label Azure) | `az network public-ip show` |
| Status saat pengamatan | `VM running` | `az vm show -d` |

## 2. Data dari sisi provider (Azure CLI)

```bash
az vm show -g AmeliaOkta_ -n VpsAmel -d --query "{name:name,size:hardwareProfile.vmSize,location:location,powerState:powerState,publicIp:publicIps,fqdn:fqdns,osDiskGB:storageProfile.osDisk.diskSizeGb,osDiskType:storageProfile.osDisk.managedDisk.storageAccountType,imageOffer:storageProfile.imageReference.offer,imageSku:storageProfile.imageReference.sku}" -o json
```

```json
{
  "fqdn": "cloudlits-amelia.australiaeast.cloudapp.azure.com",
  "imageOffer": "ubuntu-24_04-lts",
  "imageSku": "server",
  "location": "australiaeast",
  "name": "VpsAmel",
  "osDiskGB": null,
  "osDiskType": "Premium_LRS",
  "powerState": "VM running",
  "publicIp": "20.58.180.44",
  "size": "Standard_B2ats_v2"
}
```

Catatan: `osDiskGB` bernilai `null` karena ukuran disk tidak ditulis eksplisit saat VM dibuat (mengikuti ukuran bawaan image). Ukuran nyata dibuktikan dari `lsblk` (bagian 3) dan portal Disks (08-11-2026: 30 GiB).

```bash
az disk list -g AmeliaOkta_ --query "[].{name:name,sizeGb:diskSizeGb,sku:sku.name,tier:tier,iops:diskIopsReadWrite,mbps:diskMBpsReadWrite,createOption:creationData.createOption}" -o table
```

```text
Name                                            Sku          Tier    Mbps    CreateOption
----------------------------------------------  -----------  ------  ------  --------------
VpsAmel_disk1_ff04bae31ada4c98945fd4ae3607d6ab  Premium_LRS  P4      25      FromImage
```

```bash
az network public-ip show -g AmeliaOkta_ -n VpsAmel-ip --query "{ip:ipAddress,alloc:publicIPAllocationMethod,sku:sku.name,tier:sku.tier,fqdn:dnsSettings.fqdn}" -o json
```

```json
{
  "alloc": "Static",
  "fqdn": "cloudlits-amelia.australiaeast.cloudapp.azure.com",
  "ip": "20.58.180.44",
  "sku": "Standard",
  "tier": "Regional"
}
```

Aturan inbound Network Security Group:

```text
Name             Prio    Port    Src    Access    Dir
---------------  ------  ------  -----  --------  -------
SSH              300     22      *      Allow     Inbound
Allow-HTTP-80    310     80      *      Allow     Inbound
Allow-HTTPS-443  330     443     *      Allow     Inbound
```

Selain tiga aturan di atas, NSG memakai aturan bawaan Azure (`DenyAllInBound`), sehingga port lain ditolak.

## 3. Data dari dalam VM

```text
== OS ==
PRETTY_NAME="Ubuntu 24.04.5 LTS"
VERSION_ID="24.04"
7.0.0-1017-azure
cc-m03-25832072004
Tue Nov 10 22:26:48 WIB 2026
== CPU ==
2
Model name:                              AMD EPYC 7763 64-Core Processor
Thread(s) per core:                      2
Socket(s):                               1
== RAM ==
               total        used        free      shared  buff/cache   available
Mem:           887Mi       264Mi       143Mi       3.9Mi       505Mi       622Mi
Swap:          1.0Gi          0B       1.0Gi
== DISK ==
NAME     SIZE TYPE MOUNTPOINT
sda       30G disk
├─sda1    29G part /
├─sda14    4M part
├─sda15  106M part /boot/efi
└─sda16  913M part /boot
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        29G  4.0G   25G  14% /
```

### 3.1 Port yang mendengarkan

```text
*:443
*:80
0.0.0.0:22
127.0.0.1:2019
127.0.0.1:8000
127.0.0.53%lo:53
127.0.0.54:53
[::]:22
```

| Port | Proses | Terbuka ke luar? |
|---|---|---|
| 22 | OpenSSH (login key-only) | Ya (NSG + UFW) |
| 80 | Caddy, mengalihkan ke HTTPS (308) | Ya |
| 443 | Caddy, TLS Let's Encrypt | Ya |
| 8000 | Gunicorn (Flask) | **Tidak**, hanya `127.0.0.1` |
| 2019 | API admin Caddy | **Tidak**, hanya `127.0.0.1` |
| 53 | systemd-resolved (DNS lokal) | **Tidak**, hanya loopback |

### 3.2 Firewall di OS (UFW)

```text
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
22/tcp (OpenSSH)           ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
22/tcp (OpenSSH (v6))      ALLOW IN    Anywhere (v6)
80/tcp (v6)                ALLOW IN    Anywhere (v6)
443/tcp (v6)               ALLOW IN    Anywhere (v6)
```

### 3.3 Layanan

| Unit | Status |
|---|---|
| `cc-m03.service` (Gunicorn + Flask) | active |
| `caddy.service` | active (Caddy v2.11.7) |
| `cloudlits-backup.timer` | active (lihat ev05) |

## 4. Kapasitas CPU burstable (dokumentasi resmi)

Menurut Microsoft Learn, halaman "Basv2-series" (diakses 10-11-2026):

| SKU | vCPU | RAM | Base CPU performance | Initial credits | Credits banked/jam | Max banked credits |
|---|---|---|---|---|---|---|
| Standard_B2ats_v2 | 2 | 1 GiB | 20% | 60 | 24 | 576 |

Sumber: https://learn.microsoft.com/azure/virtual-machines/sizes/general-purpose/basv2-series

Artinya: VM hanya menjamin 20% kinerja CPU secara terus-menerus. Di atas itu VM memakai kredit CPU; bila kredit habis, CPU diturunkan kembali ke batas 20%. Konsekuensi untuk proyek: tugas CPU berat yang berlangsung lama (misalnya model klasifikasi FR-06) harus diuji (M11), bukan diasumsikan muat.

## 5. Kuota jaringan (dokumentasi resmi)

| Parameter | Nilai | Sumber |
|---|---|---|
| Data masuk (ingress) | Gratis | Azure Bandwidth pricing |
| Data keluar ke internet | 100 GB pertama per bulan gratis; selanjutnya USD 0,12/GB (sumber Australia, 10 TB berikutnya) | https://azure.microsoft.com/pricing/details/bandwidth/ (diakses 10-11-2026) |
| Bandwidth jaringan maksimum SKU | 6.250 Mbps | Microsoft Learn, Basv2-series |

## 6. Kecocokan dengan laporan

| Klaim di laporan (1.3, 2.3, 6.2) | Hasil 10-11-2026 | Cocok |
|---|---|---|
| Standard B2ats v2, Australia East | `Standard_B2ats_v2`, `australiaeast` | YA |
| Ubuntu Server 24.04.5 LTS, kernel 7.0.0-1017-azure | Sama | YA |
| 2 vCPU | `nproc` = 2 | YA |
| RAM 1 GiB (887 MiB terbaca) + swap 1 GiB | 887Mi + 1,0Gi | YA |
| Disk 30 GiB Premium SSD LRS P4, FromImage | `sda 30G`, Premium_LRS, P4, FromImage | YA |
| Root 29 GB, terpakai 3,9 GB (08-11) | 29G, terpakai 4,0G (14%) | YA (bertambah 0,1 GB) |
| IPv4 20.58.180.44 Static, Standard, Regional | Sama | YA |
| FQDN cloudlits-amelia.australiaeast.cloudapp.azure.com | Sama | YA |
| NSG dan UFW membuka 22, 80, 443; default deny | Sama | YA |
| Gunicorn hanya di 127.0.0.1:8000 | `127.0.0.1:8000` | YA |
| Caddy v2.11.7 | `v2.11.7` | YA |

## 7. Isu tersisa

1. **SSH terbuka untuk semua sumber.** Aturan NSG `SSH` (prioritas 300) bersumber `*`, begitu pula UFW. Mitigasi saat ini: login hanya dengan key, password dan root dinonaktifkan (laporan 1.3). Gate M04 "SSH tidak terekspos berlebihan" belum terpenuhi; opsi: batasi sumber ke IP pengelola saat bekerja, atau tutup port 22 dan gunakan Azure Run Command / Serial Console untuk administrasi.
2. **Aturan UFW untuk IPv6 aktif** walaupun VM tidak memiliki IPv6 publik. Tidak berbahaya; dapat dirapikan agar konfigurasi sesuai kondisi nyata.
3. **Screenshot portal tersanitasi belum dilampirkan** karena halaman Portal gagal memuat komponen pada 10-11-2026; bukti sisi provider diambil dari Azure CLI (bagian 2) yang memberikan data yang sama.
4. **Portal: tombol Start VM gagal tanpa pesan error** (10-11-2026); VM dinyalakan lewat `az vm start`.
