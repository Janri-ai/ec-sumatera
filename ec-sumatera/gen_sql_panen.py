"""Tab Produktivitas pemanen. python3 gen_sql_panen.py YEAR work -> work/q_pan.sql
Jalankan q_pan.sql di Snowflake, simpan array `data` hasilnya sebagai work/r_pan.json (satu string per afdeling aktif).
build.py mengubahnya ke struktur tab dan memotong bulan > END_MONTH.
Isi string: BAAFD|bulan,ton,tonB,hk,hkB,haPanen,rows,tidakBasis,basis,lebihBasis,kelasA,kelasB,kelasC,hadir,wajib;...
Definisi: basis per pemanen-hari dari INT_BASIS_TARGET (TIDAK_BASIS=1 -> tidak dapat basis; TIDAK_TARGET=1 -> basis; lainnya lebih basis);
kehadiran = KODE_ABSENSI='K' / FLAG_HK='Y' untuk KODE_KERJA='PEMANEN'; PMY = BA 2131+2122, afd B dikeluarkan; ton dari ESTATE_COST (MAX per bulan-afd)."""
import sys
y = int(sys.argv[1]); out = sys.argv[2]
BA = "('2121','2124','2131','2122')"; D = "DECODE(KODE_BA,'2122','2131',KODE_BA)"
s = f"{y}-01-01"; e = f"{y+1}-01-01"
sql = f"""WITH ec AS (SELECT {D} ba,KODE_AFD afd,DATE_TRUNC('month',BULAN)::DATE mo,MAX(TON_ACTUAL) ton,MAX(TON_BUDGET) tonb FROM PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST WHERE KODE_BA IN {BA} AND BULAN>='{s}' AND BULAN<'{e}' GROUP BY 1,2,3),
pr AS (SELECT {D} ba,KODE_AFD afd,DATE_TRUNC('month',TANGGAL_PANEN)::DATE mo,SUM(HK) hk,SUM(HA_PANEN) hap FROM PRD_DB_INTEGRATION.INT_PANEN.INT_PENCAPAIAN_PRODUKSI_PANEN WHERE KODE_BA IN {BA} AND TANGGAL_PANEN>='{s}' AND TANGGAL_PANEN<'{e}' GROUP BY 1,2,3),
hb AS (SELECT {D} ba,KODE_AFD afd,DATE_TRUNC('month',BULAN)::DATE mo,SUM(HK_BUDGET) hkb FROM PRD_DB_INTEGRATION.INT_KARYAWAN.INT_HK_BUDGET WHERE KODE_BA IN {BA} AND BULAN>='{s}' AND BULAN<'{e}' GROUP BY 1,2,3),
bt AS (SELECT {D} ba,KODE_AFD afd,DATE_TRUNC('month',TANGGAL)::DATE mo,COUNT(*) rws,SUM(IFF(TIDAK_BASIS=1,1,0)) tb,SUM(IFF(TIDAK_BASIS=0 AND TIDAK_TARGET=1,1,0)) bas,SUM(IFF(TIDAK_BASIS=0 AND TIDAK_TARGET=0,1,0)) lb,SUM(KELAS_A) ka,SUM(KELAS_B) kb,SUM(KELAS_C) kc FROM PRD_DB_INTEGRATION.INT_PANEN.INT_BASIS_TARGET WHERE KODE_BA IN {BA} AND TANGGAL>='{s}' AND TANGGAL<'{e}' GROUP BY 1,2,3),
ab AS (SELECT {D} ba,KODE_AFD afd,DATE_TRUNC('month',TANGGAL_ABSENSI)::DATE mo,SUM(IFF(KODE_ABSENSI='K',1,0)) hadir,SUM(IFF(FLAG_HK='Y',1,0)) wajib FROM PRD_DB_INTEGRATION.INT_KARYAWAN.INT_ABSENSI_HARIAN WHERE KODE_BA IN {BA} AND KODE_KERJA='PEMANEN' AND TANGGAL_ABSENSI>='{s}' AND TANGGAL_ABSENSI<'{e}' GROUP BY 1,2,3),
k AS (SELECT ba,afd,mo FROM ec UNION SELECT ba,afd,mo FROM pr UNION SELECT ba,afd,mo FROM bt UNION SELECT ba,afd,mo FROM ab),
f AS (SELECT k.ba,k.afd,TO_CHAR(k.mo,'MM') m,ROUND(COALESCE(ec.ton,0),1) ton,ROUND(COALESCE(ec.tonb,0),1) tonb,ROUND(COALESCE(pr.hk,0)) hk,ROUND(COALESCE(hb.hkb,0)) hkb,ROUND(COALESCE(pr.hap,0)) hap,COALESCE(bt.rws,0) rws,COALESCE(bt.tb,0) tb,COALESCE(bt.bas,0) bas,COALESCE(bt.lb,0) lb,COALESCE(bt.ka,0) ka,COALESCE(bt.kb,0) kb,COALESCE(bt.kc,0) kc,COALESCE(ab.hadir,0) hadir,COALESCE(ab.wajib,0) wajib FROM k LEFT JOIN ec USING(ba,afd,mo) LEFT JOIN pr USING(ba,afd,mo) LEFT JOIN hb USING(ba,afd,mo) LEFT JOIN bt USING(ba,afd,mo) LEFT JOIN ab USING(ba,afd,mo) WHERE k.afd IS NOT NULL),
act AS (SELECT ba,afd FROM f GROUP BY 1,2 HAVING SUM(hk)>0 AND NOT (ba='2131' AND afd='B'))
SELECT f.ba||f.afd||'|'||LISTAGG(f.m||','||f.ton||','||f.tonb||','||f.hk||','||f.hkb||','||f.hap||','||f.rws||','||f.tb||','||f.bas||','||f.lb||','||f.ka||','||f.kb||','||f.kc||','||f.hadir||','||f.wajib,';') WITHIN GROUP (ORDER BY f.m) FROM f JOIN act USING(ba,afd) GROUP BY f.ba,f.afd ORDER BY 1"""
open(f"{out}/q_pan.sql","w").write(sql)
