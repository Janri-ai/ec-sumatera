-- Tab Cost Element: ESTATE_COST sampai 4 tingkat (GROUP_LEVEL > LEVEL_1 > LEVEL_2 > LEVEL_3), per BA, YTD dan bulan laporan; ribu Rp.
-- PMY = 2131+2122, afd B dikeluarkan. Hanya baris dengan nilai <> 0 (aktual atau budget YTD). Ganti '2026-09-01' dan batas BULAN<.
-- Query 1 (hierarki, id urut): lihat bagian H. Query 2 (nilai per BA): LISTAGG 'id:ya,yb,ma,mb;...'
WITH src AS (SELECT DECODE(KODE_BA,'2122','2131',KODE_BA) ba, GROUP_LEVEL g, LEVEL_1 l1, LEVEL_2 l2, LEVEL_3 l3, BULAN, RP_ACTUAL a, RP_BUDGET b
 FROM PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST
 WHERE KODE_BA IN ('2121','2124','2131','2122') AND NOT (DECODE(KODE_BA,'2122','2131',KODE_BA)='2131' AND KODE_AFD='B') AND BULAN>='2026-01-01' AND BULAN<'2026-10-01'),
v AS (SELECT ba,g,l1,l2,l3, ROUND(SUM(a)/1000) ya, ROUND(SUM(b)/1000) yb, ROUND(SUM(IFF(BULAN='2026-09-01',a,0))/1000) ma, ROUND(SUM(IFF(BULAN='2026-09-01',b,0))/1000) mb FROM src GROUP BY 1,2,3,4,5),
h AS (SELECT g,l1,l2,l3, ROW_NUMBER() OVER (ORDER BY DECODE(g,'BIAYA PERAWATAN',1,'BIAYA INFRA',2,'BIAYA PEMUPUKAN',3,'BIAYA PANEN',4,'TRANSPORT PANEN',5,'BIAYA UMUM',6,'COST SEWA AMP',7,8), l1,l2,l3) id FROM (SELECT DISTINCT g,l1,l2,l3 FROM v WHERE ABS(ya)+ABS(yb)>0))
-- Query 1: SELECT id,g,l1,l2,l3 FROM h ORDER BY id;
-- Query 2: SELECT v.ba, LISTAGG(h.id||':'||v.ya||','||v.yb||','||v.ma||','||v.mb,';') WITHIN GROUP (ORDER BY h.id) FROM v JOIN h USING (g,l1,l2,l3) WHERE ABS(v.ya)+ABS(v.yb)+ABS(v.ma)+ABS(v.mb)>0 GROUP BY 1 ORDER BY 1;
SELECT 1;
