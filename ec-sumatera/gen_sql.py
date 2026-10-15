#!/usr/bin/env python3
"""Generate the Snowflake queries for the EC Region Sumatera report.

usage: python3 gen_sql.py YEAR END_MONTH [OUTDIR]
  e.g. python3 gen_sql.py 2026 9 ./work

Writes q_main.sql, q_tm.sql, q_mon.sql, q_pup.sql, q_lang.sql into OUTDIR.
Run each with the Snowflake tool and save the "data" array of each result as
JSON into OUTDIR as r_main.json, r_tm.json, r_mon.json, r_pup.json, r_lang.json.

Periods: Y = Jan..END_MONTH (YTD), M = END_MONTH (MTD), A = Jan..END_MONTH-1 (comparator).
Scope: BA 2121, 2124, 2131 (2122 = legacy code of 2131, mapped via DECODE).
Afdeling B of 2131 is dropped later in build.py (PMY = A + C); budget shares are still
computed over ALL afd of the BA so that PMY gets exactly A+C's slice of the BA budget.
"""
import sys, os, calendar

# GROUP_LEVEL values in PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST -> report category (all cost, actual and budget, come from this table)
CATS = {
    'up': "'BIAYA PERAWATAN'",
    'inf': "'BIAYA INFRA'",
    'fert': "'BIAYA PEMUPUKAN'",
    'harv': "'BIAYA PANEN'",
    'trans': "'TRANSPORT PANEN'",
    'ovh': "'BIAYA UMUM','COST SEWA AMP'",
    'depr': "'BIAYA PENYUSUTAN'",
}
K = list(CATS)
BA_IN = "('2121','2124','2131','2122')"
DBA = "DECODE(KODE_BA,'2122','2131',KODE_BA)"
DB = "PRD_DB_INTEGRATION"
EC = "PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST"


def rng(y, n):
    s = f"{y}-01-01"
    nxt = f"{y + 1}-01-01" if n == 12 else f"{y}-{n + 1:02d}-01"
    return s, nxt


def periods(y, n):
    """SELECT producing (p, s, e, n) with s/e = first day of first/last month."""
    rows = [f"SELECT 'Y' p, DATE '{y}-01-01' s, DATE '{y}-{n:02d}-01' e, {n} n",
            f"SELECT 'M', DATE '{y}-{n:02d}-01', DATE '{y}-{n:02d}-01', 1"]
    if n > 1:
        rows.append(f"SELECT 'A', DATE '{y}-01-01', DATE '{y}-{n - 1:02d}-01', {n - 1}")
    return " UNION ALL ".join(rows)


def cost_cte(y, n):
    """Cost, budget, ton and TM hectares per BA+afd+month all from ESTATE_COST (ton/ha columns repeat on every cost row of the
    same BA/afd/month, so they are taken with MAX, never SUM). Harvested ha and HK come; BBC = YTD_TON_BBC of the last harvest row on/before each month end per block (carried forward), summed per afd; month BBC = difference of consecutive month ends (the daily TON_BBC must NOT be summed, MTD_TON_BBC last-row sums are ~11% too low), all come from the integration layer."""
    s, nxt = rng(y, n)
    ca = ",".join(f"SUM(IFF(GROUP_LEVEL IN ({CATS[k]}),RP_ACTUAL,0))/1000 a_{k}" for k in K)
    cb = ",".join(f"SUM(IFF(GROUP_LEVEL IN ({CATS[k]}),RP_BUDGET,0))/1000 b_{k}" for k in K)
    return f"""
ec AS (SELECT {DBA} ba, KODE_AFD afd, DATE_TRUNC('month',BULAN)::DATE mo, {ca}, {cb}, MAX(TON_ACTUAL) ton, MAX(TON_BUDGET) tonb, MAX(HA_ACTUAL) ha, MAX(HA_BUDGET) hab FROM {EC} WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1,2,3),
pr AS (SELECT {DBA} ba, KODE_AFD afd, DATE_TRUNC('month',TANGGAL_PANEN)::DATE mo, SUM(HA_PANEN) hap, SUM(HK) hk FROM {DB}.INT_PANEN.INT_PENCAPAIAN_PRODUKSI_PANEN WHERE KODE_BA IN {BA_IN} AND TANGGAL_PANEN>='{s}' AND TANGGAL_PANEN<'{nxt}' GROUP BY 1,2,3),
bb AS (SELECT ba, afd, mo, v - COALESCE(LAG(v) OVER (PARTITION BY ba, afd ORDER BY mo), 0) bbc FROM (SELECT ba, afd, m0 mo, SUM(y) v FROM (SELECT {DBA.replace('KODE_BA','s.KODE_BA')} ba, s.KODE_AFD afd, mths.m0, s.YTD_TON_BBC y FROM {DB}.INT_PANEN.INT_PENCAPAIAN_PRODUKSI_PANEN s JOIN (SELECT DATEADD(month,seq4(),'{s}'::DATE) m0 FROM TABLE(GENERATOR(ROWCOUNT=>{n}))) mths ON s.TANGGAL_PANEN<=LAST_DAY(mths.m0) WHERE s.KODE_BA IN {BA_IN} AND s.TANGGAL_PANEN>='{s}' QUALIFY ROW_NUMBER() OVER (PARTITION BY s.KODE_BA,s.KODE_AFD,s.KODE_BLOK,mths.m0 ORDER BY s.TANGGAL_PANEN DESC)=1) GROUP BY 1,2,3)),
hb AS (SELECT {DBA} ba, KODE_AFD afd, DATE_TRUNC('month',BULAN)::DATE mo, SUM(HK_BUDGET) hkb FROM {DB}.INT_KARYAWAN.INT_HK_BUDGET WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1,2,3),
keys AS (SELECT ba,afd,mo FROM ec UNION SELECT ba,afd,mo FROM pr UNION SELECT ba,afd,mo FROM hb UNION SELECT ba,afd,mo FROM bb),
f AS (SELECT k.ba,k.afd,k.mo, COALESCE(ec.ton,0) ton, COALESCE(bb.bbc,0) bbc, COALESCE(pr.hap,0) hap, COALESCE(pr.hk,0) hk, COALESCE(ec.tonb,0) tonb, COALESCE(hb.hkb,0) hkb, COALESCE(ec.ha,0) ha, COALESCE(ec.hab,0) hab, {",".join(f"COALESCE(ec.a_{k},0) a_{k}" for k in K)}, {",".join(f"COALESCE(ec.b_{k},0) b_{k}" for k in K)} FROM keys k LEFT JOIN ec ON ec.ba=k.ba AND ec.afd=k.afd AND ec.mo=k.mo LEFT JOIN pr ON pr.ba=k.ba AND pr.afd=k.afd AND pr.mo=k.mo LEFT JOIN bb ON bb.ba=k.ba AND bb.afd=k.afd AND bb.mo=k.mo LEFT JOIN hb ON hb.ba=k.ba AND hb.afd=k.afd AND hb.mo=k.mo WHERE k.afd IS NOT NULL)"""


def q_bbc(y, n):
    """Only ba,afd,p,bbc - used to refresh column 4 of r_main.json without re-pulling everything."""
    return f"""WITH {cost_cte(y, n)},
pd AS ({periods(y, n)})
SELECT ba,afd,pd.p, ROUND(SUM(bbc),1) FROM f JOIN pd ON f.mo BETWEEN pd.s AND pd.e GROUP BY 1,2,3 ORDER BY 1,2,3"""


def q_main(y, n):
    agg = ",".join(f"ROUND(SUM(a_{k}),0)" for k in K) + "," + ",".join(f"ROUND(SUM(b_{k}),0)" for k in K)
    return f"""WITH {cost_cte(y, n)},
pd AS ({periods(y, n)})
SELECT ba,afd,pd.p, ROUND(SUM(ton),1),ROUND(SUM(bbc),1),ROUND(SUM(hap),1),ROUND(SUM(hk),1),ROUND(SUM(tonb),1),ROUND(SUM(hkb),1),ROUND(SUM(ha)/MAX(pd.n),1),ROUND(SUM(hab)/MAX(pd.n),1),{agg}
FROM f JOIN pd ON f.mo BETWEEN pd.s AND pd.e GROUP BY 1,2,3 ORDER BY 1,2,3"""


def q_mon(y, n):
    """Monthly BA series (afd B of 2131 excluded -> consistent with PMY = A+C)."""
    tot_a = "+".join(f"a_{k}" for k in K)
    tot_b = "+".join(f"b_{k}" for k in K)
    return f"""WITH {cost_cte(y, n)}
SELECT ba, TO_CHAR(mo,'YYYY-MM') m, ROUND(SUM({tot_a}),0) cost, ROUND(SUM({tot_b}),0) bud, ROUND(SUM(ton),1) ton, ROUND(SUM(bbc),1) bbc
FROM f WHERE NOT (ba='2131' AND afd='B') GROUP BY 1,2 ORDER BY 1,2"""


def q_tm(y, n):
    """Per BA/afd/period: harvested area (HEKTAR_PANEN, monthly average) and ton harvested from TM blocks (for Yield TM).
    Columns: ba, afd, p, hapan, tontm. Not cost data, so from the integration layer."""
    s, nxt = rng(y, n)
    return f"""WITH
blk AS (SELECT {DBA} ba, KODE_AFD afd, KODE_BLOK blok, DATE_TRUNC('month',BULAN)::DATE mo,
  MAX(IFF(MATURITY_STATUS='TM' AND KATEGORI_TANAH='PLANTED',1,0)) tm
  FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1,2,3,4),
har AS (SELECT {DBA} ba, KODE_AFD afd, DATE_TRUNC('month',BULAN)::DATE mo, SUM(COALESCE(HEKTAR_PANEN,0)) hapan
  FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1,2,3),
tonm AS (SELECT {DBA.replace('KODE_BA','p.KODE_BA')} ba, p.KODE_AFD afd, DATE_TRUNC('month',p.TANGGAL_PANEN)::DATE mo, SUM(IFF(b.tm=1,p.TON_AKTUAL,0)) tontm
  FROM {DB}.INT_PANEN.INT_PENCAPAIAN_PRODUKSI_PANEN p LEFT JOIN blk b ON b.ba={DBA.replace('KODE_BA','p.KODE_BA')} AND b.afd=p.KODE_AFD AND b.blok=p.KODE_BLOK AND b.mo=DATE_TRUNC('month',p.TANGGAL_PANEN)::DATE
  WHERE p.KODE_BA IN {BA_IN} AND p.TANGGAL_PANEN>='{s}' AND p.TANGGAL_PANEN<'{nxt}' GROUP BY 1,2,3),
mm AS (SELECT har.ba, har.afd, har.mo, har.hapan, COALESCE(t.tontm,0) tontm FROM har LEFT JOIN tonm t ON t.ba=har.ba AND t.afd=har.afd AND t.mo=har.mo),
pd AS ({periods(y, n)})
SELECT mm.ba, mm.afd, pd.p, ROUND(SUM(hapan)/MAX(pd.n),1) hapan, ROUND(SUM(tontm),1) tontm
FROM mm JOIN pd ON mm.mo BETWEEN pd.s AND pd.e GROUP BY mm.ba, mm.afd, pd.p ORDER BY 1,2,3"""


def q_pup(y, n):
    """Fertilizer target (INT_PUPUK_TARGET) vs actual kg (INT_PUPUK_HARIAN) per BA, afd and type, TM blocks only.
    Columns: ba, afd, jenis, tgt_tm, act_tm, tgt_nontm, act_nontm, tgt_fy_tm.
    tgt_tm/act_tm = YTD Jan..n on TM blocks (target STATUS 'TM%' / actual STATUS_MATURITY = 'TM'); *_nontm = the rest (TBM, blank), reported
    so the page can state what was excluded; tgt_fy_tm = TM target for the FULL year Jan..Dec (recommendation is a full-year plan)."""
    s, nxt = rng(y, n)
    ye = f"{y+1}-01-01"
    return f"""WITH t AS (SELECT {DBA} ba, KODE_AFD afd, JENIS_PUPUK j, SUM(IFF(STATUS LIKE 'TM%' AND BULAN<'{nxt}',TARGET_KG,0)) tm, SUM(IFF(COALESCE(STATUS,'') LIKE 'TM%' OR BULAN>='{nxt}',0,TARGET_KG)) nontm, SUM(IFF(STATUS LIKE 'TM%',TARGET_KG,0)) fy FROM {DB}.INT_RAWAT.INT_PUPUK_TARGET WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{ye}' GROUP BY 1,2,3),
h AS (SELECT {DBA} ba, KODE_AFD afd, NAMA_PUPUK j, SUM(IFF(STATUS_MATURITY='TM',KG_AKTUAL,0)) tm, SUM(IFF(COALESCE(STATUS_MATURITY,'')='TM',0,KG_AKTUAL)) nontm FROM {DB}.INT_RAWAT.INT_PUPUK_HARIAN WHERE KODE_BA IN {BA_IN} AND TANGGAL_PUPUK>='{s}' AND TANGGAL_PUPUK<'{nxt}' GROUP BY 1,2,3)
SELECT COALESCE(t.ba,h.ba) ba, COALESCE(t.afd,h.afd) afd, COALESCE(t.j,h.j) j, ROUND(COALESCE(t.tm,0)) tgt_tm, ROUND(COALESCE(h.tm,0)) act_tm, ROUND(COALESCE(t.nontm,0)) tgt_nontm, ROUND(COALESCE(h.nontm,0)) act_nontm, ROUND(COALESCE(t.fy,0)) tgt_fy
FROM t FULL OUTER JOIN h ON t.ba=h.ba AND t.afd=h.afd AND t.j=h.j WHERE COALESCE(t.fy,0)<>0 OR COALESCE(t.nontm,0)<>0 OR COALESCE(h.tm,0)<>0 OR COALESCE(h.nontm,0)<>0 ORDER BY 1,2,3"""


def q_pok(y, n):
    """Average monthly TM hectares / palms per BA+afd: YTD (Jan..n) and full year (Jan..Dec, uses planned maturity changes).
    Columns: ba, afd, ha_ytd, pokok_ytd, ha_fy, pokok_fy."""
    s, nxt = rng(y, n)
    ye = f"{y+1}-01-01"
    return f"""WITH m AS (SELECT {DBA} ba, KODE_AFD afd, DATE_TRUNC('month',BULAN)::DATE mo, SUM(IFF(MATURITY_STATUS='TM' AND KATEGORI_TANAH='PLANTED',HEKTAR,0)) ha, SUM(IFF(MATURITY_STATUS='TM' AND KATEGORI_TANAH='PLANTED',COALESCE(JML_POKOK,0),0)) pk FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{ye}' GROUP BY 1,2,3)
SELECT ba, afd, ROUND(AVG(IFF(mo<'{nxt}',ha,NULL)),2) ha_ytd, ROUND(AVG(IFF(mo<'{nxt}',pk,NULL))) pokok_ytd, ROUND(AVG(ha),2) ha_fy, ROUND(AVG(pk)) pokok_fy FROM m GROUP BY 1,2 ORDER BY 1,2"""


def q_lang(y, n):
    """Langsir TBS cost (Rp ribu): YTD and MTD per BA, from ESTATE_COST (LEVEL_1 = 'LANGSIR'). Afd B of 2131 excluded."""
    s, nxt = rng(y, n)
    m = f"{y}-{n:02d}-01"
    return f"""SELECT {DBA} ba, ROUND(SUM(RP_ACTUAL)/1000) ytd, ROUND(SUM(IFF(DATE_TRUNC('month',BULAN)::DATE='{m}',RP_ACTUAL,0))/1000) mtd
FROM {EC} WHERE KODE_BA IN {BA_IN} AND NOT ({DBA}='2131' AND KODE_AFD='B') AND LEVEL_1='LANGSIR' AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1 ORDER BY 1"""


def q_hs(y, n):
    """Hectare Statement per BA/afd/tahun tanam/status at the END of month n, from INT_HEKTAR_BLOK (block level).
    Columns: ba, afd, thn, ms, kt, ha, pokok, nblok, bibit (progeni). kt = KATEGORI_TANAH (PLANTED / UNPLANTABLE / ...). Rows with HEKTAR = 0 dropped."""
    m = f"{y}-{n:02d}-01"
    return f"""SELECT {DBA} ba, KODE_AFD afd, COALESCE(NULLIF(TAHUN_TANAM,''),'-') thn, COALESCE(NULLIF(MATURITY_STATUS,''),'-') ms, KATEGORI_TANAH kt,
  ROUND(SUM(HEKTAR),2) ha, ROUND(SUM(COALESCE(JML_POKOK,0))) pokok, COUNT(*) nblok, COALESCE(NULLIF(BIBIT,''),'-') bibit
FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK WHERE KODE_BA IN {BA_IN} AND DATE_TRUNC('month',BULAN)='{m}' AND HEKTAR>0
GROUP BY 1,2,3,4,5,9 ORDER BY 1,2,3,4,9"""


def q_hstm(y, n):
    """TM hectares (PLANTED, MATURITY_STATUS TM*) per BA/afd and month-end from INT_HEKTAR_BLOK (= Hectare Statement). Columns: ba, afd, m, ha.
    The report divides per-Ha costs by this (HS TM at the last month of the period; period A uses month n-1)."""
    s, nxt = rng(y, n)
    return f"""SELECT {DBA} ba, KODE_AFD afd, MONTH(BULAN) m, ROUND(SUM(IFF(UPPER(MATURITY_STATUS) LIKE 'TM%' AND KATEGORI_TANAH='PLANTED',HEKTAR,0)),2) ha
FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1,2,3
HAVING SUM(IFF(UPPER(MATURITY_STATUS) LIKE 'TM%' AND KATEGORI_TANAH='PLANTED',HEKTAR,0))>0 ORDER BY 1,2,3"""


def q_ptt(y, n):
    """Production (ton, TON_AKTUAL) and harvested area per BA/afd/tahun tanam/maturity status, block level:
    INT_PENCAPAIAN_PRODUKSI_PANEN joined to INT_HEKTAR_BLOK of the same block-month (planting year and status as in the Hectare Statement of that month).
    Columns: ba, afd, thn, ms, ton_a (months < n), ton_m (month n), hp_a (sum of monthly HEKTAR_PANEN, months < n), hp_m (month n).
    Blocks without an HS row for a month get thn/ms = '?'. Period Y: ton = a+m, ha panen = (hp_a+hp_m)/n; period A: ton = a, ha = hp_a/(n-1); period M: m."""
    s, nxt = rng(y, n)
    m = f"{y}-{n:02d}-01"
    return f"""WITH blk AS (SELECT {DBA} ba, KODE_AFD afd, KODE_BLOK blok, DATE_TRUNC('month',BULAN)::DATE mo, MAX(COALESCE(NULLIF(TAHUN_TANAM,''),'?')) thn, MAX(COALESCE(NULLIF(MATURITY_STATUS,''),'?')) ms, SUM(COALESCE(HEKTAR_PANEN,0)) hp
  FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1,2,3,4),
tn AS (SELECT {DBA} ba, KODE_AFD afd, KODE_BLOK blok, DATE_TRUNC('month',TANGGAL_PANEN)::DATE mo, SUM(TON_AKTUAL) ton
  FROM {DB}.INT_PANEN.INT_PENCAPAIAN_PRODUKSI_PANEN WHERE KODE_BA IN {BA_IN} AND TANGGAL_PANEN>='{s}' AND TANGGAL_PANEN<'{nxt}' GROUP BY 1,2,3,4)
SELECT COALESCE(b.ba,t.ba) ba, COALESCE(b.afd,t.afd) afd, COALESCE(b.thn,'?') thn, COALESCE(b.ms,'?') ms,
  ROUND(SUM(IFF(COALESCE(b.mo,t.mo)<'{m}',COALESCE(t.ton,0),0)),2) ton_a, ROUND(SUM(IFF(COALESCE(b.mo,t.mo)='{m}',COALESCE(t.ton,0),0)),2) ton_m,
  ROUND(SUM(IFF(COALESCE(b.mo,t.mo)<'{m}',COALESCE(b.hp,0),0)),2) hp_a, ROUND(SUM(IFF(COALESCE(b.mo,t.mo)='{m}',COALESCE(b.hp,0),0)),2) hp_m
FROM blk b FULL OUTER JOIN tn t ON b.ba=t.ba AND b.afd=t.afd AND b.blok=t.blok AND b.mo=t.mo
GROUP BY 1,2,3,4 HAVING SUM(COALESCE(t.ton,0))<>0 OR SUM(COALESCE(b.hp,0))<>0 ORDER BY 1,2,3,4"""


def q_hsavg(y, n):
    """Planted hectares per BA/afd/tahun tanam and status group (TM, TBM = TBM 2 + 3, X = other) from INT_HEKTAR_BLOK, split for monthly averages.
    Columns: ba, afd, thn, kind, ha_a (sum of monthly ha, months < n), ha_m (month n). Average ha: Y = (ha_a+ha_m)/n, A = ha_a/(n-1), M = ha_m."""
    s, nxt = rng(y, n)
    m = f"{y}-{n:02d}-01"
    return f"""WITH x AS (SELECT {DBA} ba, KODE_AFD afd, COALESCE(NULLIF(TAHUN_TANAM,''),'-') thn,
  CASE WHEN UPPER(MATURITY_STATUS) LIKE 'TM%' THEN 'TM' WHEN REPLACE(UPPER(MATURITY_STATUS),' ','') IN ('TBM2','TBM3') THEN 'TBM' ELSE 'X' END kind,
  DATE_TRUNC('month',BULAN)::DATE mo, SUM(HEKTAR) ha
  FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK WHERE KODE_BA IN {BA_IN} AND KATEGORI_TANAH='PLANTED' AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1,2,3,4,5)
SELECT ba, afd, thn, kind, ROUND(SUM(IFF(mo<'{m}',ha,0)),2) ha_a, ROUND(SUM(IFF(mo='{m}',ha,0)),2) ha_m FROM x GROUP BY 1,2,3,4 HAVING SUM(ha)>0 ORDER BY 1,2,3,4"""


def _bd(y, n):
    """Progeni dominan per blok: BIBIT dengan HEKTAR terbesar pada bulan terakhir yang ada (PLANTED), Jan..n. (Per September 2026 tidak ada blok dengan >1 progeni.)"""
    s, nxt = rng(y, n)
    return f"""bd AS (SELECT {DBA} ba, KODE_AFD afd, KODE_BLOK blok, COALESCE(NULLIF(BIBIT,''),'-') bibit FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK
  WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{nxt}' AND KATEGORI_TANAH='PLANTED'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY {DBA},KODE_AFD,KODE_BLOK ORDER BY DATE_TRUNC('month',BULAN) DESC, HEKTAR DESC, BIBIT)=1)"""


def q_ptt_pg(y, n):
    """Seperti q_ptt tetapi dipecah per progeni dominan blok. Columns: ba, afd, thn, ms, bibit, ton_a, ton_m, hp_a, hp_m. Disimpan sebagai work/r_ptt_pg.json ([ba,afd,thn,ms,ton_a,ton_m,hp_a,hp_m,bibit])."""
    s, nxt = rng(y, n)
    m = f"{y}-{n:02d}-01"
    return f"""WITH {_bd(y, n)},
blk AS (SELECT {DBA} ba, KODE_AFD afd, KODE_BLOK blok, DATE_TRUNC('month',BULAN)::DATE mo, MAX(COALESCE(NULLIF(TAHUN_TANAM,''),'?')) thn, MAX(COALESCE(NULLIF(MATURITY_STATUS,''),'?')) ms, SUM(COALESCE(HEKTAR_PANEN,0)) hp
  FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK WHERE KODE_BA IN {BA_IN} AND BULAN>='{s}' AND BULAN<'{nxt}' GROUP BY 1,2,3,4),
tn AS (SELECT {DBA} ba, KODE_AFD afd, KODE_BLOK blok, DATE_TRUNC('month',TANGGAL_PANEN)::DATE mo, SUM(TON_AKTUAL) ton
  FROM {DB}.INT_PANEN.INT_PENCAPAIAN_PRODUKSI_PANEN WHERE KODE_BA IN {BA_IN} AND TANGGAL_PANEN>='{s}' AND TANGGAL_PANEN<'{nxt}' GROUP BY 1,2,3,4),
j AS (SELECT COALESCE(b.ba,t.ba) ba, COALESCE(b.afd,t.afd) afd, COALESCE(b.blok,t.blok) blok, COALESCE(b.thn,'?') thn, COALESCE(b.ms,'?') ms, COALESCE(b.mo,t.mo) mo, t.ton, b.hp FROM blk b FULL OUTER JOIN tn t ON b.ba=t.ba AND b.afd=t.afd AND b.blok=t.blok AND b.mo=t.mo)
SELECT j.ba, j.afd, j.thn, j.ms, COALESCE(bd.bibit,'-') bibit,
  ROUND(SUM(IFF(j.mo<'{m}',COALESCE(j.ton,0),0)),2) ton_a, ROUND(SUM(IFF(j.mo='{m}',COALESCE(j.ton,0),0)),2) ton_m,
  ROUND(SUM(IFF(j.mo<'{m}',COALESCE(j.hp,0),0)),2) hp_a, ROUND(SUM(IFF(j.mo='{m}',COALESCE(j.hp,0),0)),2) hp_m
FROM j LEFT JOIN bd ON bd.ba=j.ba AND bd.afd=j.afd AND bd.blok=j.blok GROUP BY 1,2,3,4,5 HAVING SUM(COALESCE(j.ton,0))<>0 OR SUM(COALESCE(j.hp,0))<>0 ORDER BY 1,2,3,4,5"""


def q_hsavg_pg(y, n):
    """Seperti q_hsavg tetapi dipecah per progeni dominan blok. Columns: ba, afd, thn, kind, bibit, ha_a, ha_m. Disimpan sebagai work/r_hsavg_pg.json ([ba,afd,thn,kind,ha_a,ha_m,bibit])."""
    s, nxt = rng(y, n)
    m = f"{y}-{n:02d}-01"
    return f"""WITH {_bd(y, n)},
x AS (SELECT {DBA.replace('KODE_BA','h.KODE_BA')} ba, h.KODE_AFD afd, COALESCE(NULLIF(h.TAHUN_TANAM,''),'-') thn,
  CASE WHEN UPPER(h.MATURITY_STATUS) LIKE 'TM%' THEN 'TM' WHEN REPLACE(UPPER(h.MATURITY_STATUS),' ','') IN ('TBM2','TBM3') THEN 'TBM' ELSE 'X' END kind,
  COALESCE(bd.bibit,'-') bibit, DATE_TRUNC('month',h.BULAN)::DATE mo, SUM(h.HEKTAR) ha
  FROM {DB}.INT_PANEN.INT_HEKTAR_BLOK h LEFT JOIN bd ON bd.ba={DBA.replace('KODE_BA','h.KODE_BA')} AND bd.afd=h.KODE_AFD AND bd.blok=h.KODE_BLOK
  WHERE h.KODE_BA IN {BA_IN} AND h.KATEGORI_TANAH='PLANTED' AND h.BULAN>='{s}' AND h.BULAN<'{nxt}' GROUP BY 1,2,3,4,5,6)
SELECT ba, afd, thn, kind, bibit, ROUND(SUM(IFF(mo<'{m}',ha,0)),2) ha_a, ROUND(SUM(IFF(mo='{m}',ha,0)),2) ha_m FROM x GROUP BY 1,2,3,4,5 HAVING SUM(ha)>0 ORDER BY 1,2,3,4,5"""


if __name__ == '__main__':
    y, n = int(sys.argv[1]), int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else '.'
    os.makedirs(out, exist_ok=True)
    for name, fn in (('main', q_main), ('tm', q_tm), ('mon', q_mon), ('pup', q_pup), ('pok', q_pok), ('lang', q_lang), ('bbc', q_bbc), ('hs', q_hs), ('hsavg', q_hsavg), ('hs0', lambda y, n: q_hs(y, n - 1)), ('hstm', q_hstm), ('ptt', q_ptt), ('ptt_pg', q_ptt_pg), ('hsavg_pg', q_hsavg_pg)):
        sql = " ".join(fn(y, n).split())
        open(os.path.join(out, f'q_{name}.sql'), 'w').write(sql)
        print(name, len(sql))
