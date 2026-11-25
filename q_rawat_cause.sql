-- Penyebab selisih Perawatan: per BA, LEVEL_1, LEVEL_2 (ribu Rp, YTD). Pembanding per sel afd x LEVEL_3 (GROUP_LEVEL='BIAYA PERAWATAN').
-- unbudgeted = aktual di sel tanpa budget; over = (aktual-budget) di sel aktual>budget>0; under = (budget-aktual) di sel aktual<budget. Identitas: aktual-budget = unb+over-under.
-- Ganti batas BULAN< sesuai periode. Hasil (satu baris per string 'ba|L1|L2|a|b|unb|over|under') -> work/rawcause.txt, lalu rawcause_load.py work.
WITH s AS (SELECT DECODE(KODE_BA,'2122','2131',KODE_BA) ba, KODE_AFD afd, LEVEL_1 l1, LEVEL_2 l2, LEVEL_3 l3, SUM(RP_ACTUAL)/1000 a, SUM(RP_BUDGET)/1000 b FROM PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST WHERE KODE_BA IN ('2121','2124','2131','2122') AND NOT (DECODE(KODE_BA,'2122','2131',KODE_BA)='2131' AND KODE_AFD='B') AND BULAN>='2026-01-01' AND BULAN<'2026-11-01' AND GROUP_LEVEL='BIAYA PERAWATAN' GROUP BY 1,2,3,4,5)
SELECT ba||'|'||l1||'|'||l2||'|'||ROUND(SUM(a))||'|'||ROUND(SUM(b))||'|'||ROUND(SUM(IFF(b=0 AND a>0,a,0)))||'|'||ROUND(SUM(IFF(b>0 AND a>b,a-b,0)))||'|'||ROUND(SUM(IFF(b>0 AND a<b,b-a,0))) r
FROM s GROUP BY ba,l1,l2 HAVING SUM(a)<>0 OR SUM(b)<>0 ORDER BY ba,l1,l2;
