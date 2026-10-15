-- Norma HK/Ha dari BUDGET GUIDELINES 2025 (sheet VIII - TM, kolom QTY = HK per Ha per rotasi, baris mineral/datar) dipetakan ke aktivitas harian TM.
-- Pembanding sebasis: hanya aktivitas TM berstatuan Ha yang punya norma. Per afd x Level 1: [Ha, HK, HK norma (=jumlah Ha x norma)] YTD lalu bulan laporan.
-- Hasil kolom j -> rawnorm_load.py -> work/r_rawnorm.json. Ganti '2026-09-01' dan batas tanggal sesuai bulan laporan.
WITH nm AS (SELECT column1 k, column2 n, column3 i FROM VALUES
('MANUAL CIRCLE WEEDING',2.0,5),('CPT SPRAYING KNAPSACK',0.4,5),('CPT SPRAYING MHS',0.2,5),
('SPOT SPRAYING',0.4,4),('SPOT SPRAYING - ELIMINASI',0.15,4),('DONGKEL ANAK KAYU',1.0,4),('DONGKEL ANAK KAYU - ELIMINASI',0.1,4),('SEMPROT KENTOSAN',0.4,4),
('SPOT LALANG',0.15,1),
('BENEFICIAL PLANTS AND UPKEEP',0.25,0),('PEST & DISEASE DETECTION',0.03,0),('OTHER PESTS & DISEASES CTRL',0.19,0),
('BLACK BUNCH CENSUS (BBC)',0.06,6),('SPH CENSUS',0.1,6),('LEAF SAMPLING',0.15,6),('SOIL SAMPLING',0.05,6)),
h AS (SELECT DECODE(KODE_BA,'2122','2131',KODE_BA) ba, KODE_AFD afd, TANGGAL_RAWAT d, NIK_KARYAWAN nik, HASIL_AKTIFITAS ha,
 REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(UPPER(NAMA_AKTIFITAS),'^TM - ',''),' *- *(LABORS?|PIECE RATED|CONTRACTS?)$',''),'/ ','/') k
 FROM PRD_DB_INTEGRATION.INT_RAWAT.INT_RAWAT_HARIAN WHERE KODE_BA IN ('2121','2124','2131','2122') AND NOT (DECODE(KODE_BA,'2122','2131',KODE_BA)='2131' AND KODE_AFD='B') AND TANGGAL_RAWAT>='2026-01-01' AND TANGGAL_RAWAT<'2026-10-01' AND UOM_AKTIFITAS='HA' AND UPPER(NAMA_AKTIFITAS) LIKE 'TM - %'),
hm AS (SELECT h.*, nm.n, nm.i FROM h JOIN nm ON h.k=nm.k)
SELECT ba, afd, OBJECT_AGG(i::STRING, ARRAY_CONSTRUCT(ROUND(ha_y,1),hk_y,ROUND(ex_y,1),ROUND(ha_m,1),hk_m,ROUND(ex_m,1)))::STRING j FROM
 (SELECT ba, afd, i, SUM(ha) ha_y, COUNT(DISTINCT nik||d) hk_y, SUM(ha*n) ex_y, SUM(IFF(d>='2026-09-01',ha,0)) ha_m, COUNT(DISTINCT IFF(d>='2026-09-01',nik||d,NULL)) hk_m, SUM(IFF(d>='2026-09-01',ha*n,0)) ex_m FROM hm GROUP BY 1,2,3)
GROUP BY 1,2 ORDER BY 1,2;
