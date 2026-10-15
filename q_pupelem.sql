-- Tab Pemupukan: biaya pemupukan (GROUP_LEVEL='BIAYA PEMUPUKAN') per elemen biaya (akhiran LEVEL_3), YTD, per BA; ribu Rp. PMY = 2131+2122, afd B dikeluarkan.
-- Elemen: Material, Labors (HK), Transports, Contracts, Tools, Lainnya (Fertilizer Averaged Out, Supervision, dst). Ganti batas BULAN< sesuai periode.
SELECT DECODE(KODE_BA,'2122','2131',KODE_BA) ba,
 CASE WHEN LEVEL_3 LIKE '%- Materials' THEN 'M' WHEN LEVEL_3 LIKE '%- Labors' THEN 'L' WHEN LEVEL_3 LIKE '%- Transports' THEN 'T' WHEN LEVEL_3 LIKE '%- Contracts' THEN 'C' WHEN LEVEL_3 LIKE '%- Tools' THEN 'A' ELSE 'X' END el,
 ROUND(SUM(RP_ACTUAL)/1000) ya, ROUND(SUM(RP_BUDGET)/1000) yb
FROM PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST
WHERE GROUP_LEVEL='BIAYA PEMUPUKAN' AND KODE_BA IN ('2121','2124','2131','2122') AND NOT (DECODE(KODE_BA,'2122','2131',KODE_BA)='2131' AND KODE_AFD='B') AND BULAN>='2026-01-01' AND BULAN<'2026-10-01'
GROUP BY 1,2 ORDER BY 1,2;
