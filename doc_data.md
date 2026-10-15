# EC Sumatera — ketersediaan data di Snowflake vs template EC Kaltim 3 (diperbarui 6 Okt 2026)

Template: folder "EC PROJECT CONTOH" (EC YWA/AAPA/GAS/NPN.xlsx, REKAP EC ALL.xlsx, deck "EC Kaltim 3 New", periode YTD Des 2022). Sumber data Kaltim 3 = Clickview/One Click. Sumber Snowflake: PRD_DB_INTEGRATION. Laporan web yang sudah dibangun dan cara update-nya: lihat `claude/ec-sumatera/PLAYBOOK.md`.

## Cakupan Sumatera (INT_MASTER_BA, region 02)
Hanya 1 PT: BBB (kode 21, Jambi). BA sawit: 2121 Sekernan Estate (SEK), 2124 Sawit Brahma (SBR), 2131 Pemayung (PMY), 2132 Aksodano 1, 2133 Danobangko (mulai 2025). Laporan hanya memuat 2121, 2124, 2131. Non-sawit: 2123 Karet Sekernan, 2141 Mill, 2142 RSS Mill. Ranking antar-PT tidak bisa direplikasi; ranking per afdeling.

## Status per kebutuhan
| Kebutuhan template | Sumber Snowflake | Status |
|---|---|---|
| Luasan per afd (TM/TBM) | INT_PANEN.INT_HEKTAR_BLOK (HEKTAR, HEKTAR_PANEN, HEKTAR_BUDGET, MATURITY_STATUS, KATEGORI_TANAH; BULAN = akhir bulan, pakai DATE_TRUNC) | Tersedia 2012-2026 |
| Produksi aktual | INT_PENCAPAIAN_PRODUKSI_PANEN (= INT_PANEN_HARIAN_AKTUAL, total identik) | Tersedia. TON_BBC tidak dapat dipakai (capaian 454%) |
| Target produksi / HK budget | INT_KARYAWAN.INT_HK_BUDGET (TON_BUDGET, HK_BUDGET per afd) | Tersedia; ada baris tahun salah (2027, 3019) |
| Biaya aktual per afd | INT_COST.INT_COST_ACTUAL_BUDGET (GROUP_COA_LV1 = aktivitas) | Tersedia; tanpa kolom maturity |
| Budget biaya | INT_COST.INT_COST_BUDGET | Hanya level BA per bulan (SOURCE_BUDGET='ESTATE_COST'); dialokasikan ke afd dengan asumsi (lihat playbook). OPEX_BIAYA_UMUM jangan dijumlah (double count) |
| Biaya per blok (untuk porsi TM/TBM) | INT_COST.INT_COST_ALOKASI (COA, AMOUNT, KODE_BLOK) | Tersedia bulanan; COA dipetakan ke kategori lewat INT_COST_ACTUAL_BUDGET |
| Pupuk aktual vs rekomendasi | INT_RAWAT.INT_PUPUK_HARIAN (KG_AKTUAL, MATERIAL_PRICE, STATUS_MATURITY), INT_PUPUK_TARGET (TARGET_KG) | Tersedia; ACTUAL_KG di PUPUK_TARGET selalu 0 (jangan dipakai) |
| Langsir TBS | GROUP_COA_LV1 = 'LANGSIR TBS' (biaya saja) | Biaya tersedia; KM langsir tidak |
| VRA Rp/KM per unit | - | BELUM tersedia (biaya per kendaraan tidak ditemukan) |
| RKB vs PDB | - | Belum tersedia / definisi belum jelas |

## BA 2122 dan Pemayung (temuan terverifikasi)
- 2122 adalah kode lama 2131 (dikonfirmasi pemilik data). Muncul hanya di biaya aktual dan budget biaya; HK_BUDGET 2122 hanya ada 2014-2019. Budget biaya 2025 ada di KEDUANYA (2122 dan 2131) -> risiko double count. Selalu pakai DECODE(KODE_BA,'2122','2131',KODE_BA).
- Aturan laporan: afdeling Pemayung dinamai "PMY" = afd A + afd C 2131; afd B dikeluarkan penuh (budget ton B ~1.562 t, 182 ha). Budget ton PMY jadi 4.212 sesuai laporan user (bukan 5.774 dari total BA 2131).
- Catatan koreksi: klaim lama "luas 2131 turun ~38% di 2025" tidak terbukti dan dihapus; perbedaan luas lebih mungkin akibat pemisahan afd B/C dan status TM vs TBM.

## Jebakan data
- Data sumber bisa direvisi mundur (contoh: produksi SBR afd C Juli 2026 turun 26,0 t setelah pull pertama; YTD Sep SBR 32.386,0 t, bukan 32.412,0 t). Selalu tarik ulang penuh.
- Biaya bulan terakhir sering belum lengkap (penyusutan Rp 0 di semua BA pada Sep 2026; OVH SBR afd B-D dan PMY hampir nol).
- INT_COST_ACTUAL_BUDGET: kolom ACTIVITY berisi status ('TM'); nama aktivitas ada di GROUP_COA_LV1.
- Actual negatif di 2026 untuk 2132 dan 2133 (reversal).
- SBR punya ~30% biaya pupuk dan panen di blok TBM 3, sehingga biaya TM-only jauh lebih kecil dari total.
