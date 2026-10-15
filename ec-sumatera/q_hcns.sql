-- Head Count Non-Staff (MPE) Sekernan 2121 vs Brahma Sawit 2124 + Karet 2123. Sumber: INT_KARYAWAN.INT_MPE (JOB_CODE kosong di semua baris -> pakai JOB_DESCRIPTION + JOB_TYPE).
-- BULAN > bulan berjalan di INT_MPE hanya salinan proyeksi (jumlah datar) -> jangan dipakai. LOCATION = kode BA.
-- 1) detail jabatan, bulan yang ditampilkan (contoh Sep dan Okt 2026) -> simpan ke work/hcns.txt di bawah baris '#detail'
SELECT TO_CHAR(BULAN,'MM')||'|'||COALESCE(JOB_TYPE,'')||'|'||REPLACE(TRIM(JOB_DESCRIPTION),'|','/')||'|'||COUNT_IF(LOCATION='2121')||'|'||COUNT_IF(LOCATION='2124')||'|'||COUNT_IF(LOCATION='2123') AS line
FROM PRD_DB_INTEGRATION.INT_KARYAWAN.INT_MPE WHERE LOCATION IN ('2121','2123','2124') AND BULAN IN ('2026-09-30','2026-10-31')
GROUP BY BULAN, JOB_TYPE, TRIM(JOB_DESCRIPTION) ORDER BY BULAN, JOB_TYPE, TRIM(JOB_DESCRIPTION);
-- 2) status karyawan per bulan (Des tahun lalu s/d bulan berjalan) -> di bawah baris '#kelas'
SELECT TO_CHAR(BULAN,'MM')||'|'||EMPL_CLASS||'|'||COUNT_IF(LOCATION='2121')||'|'||COUNT_IF(LOCATION='2124')||'|'||COUNT_IF(LOCATION='2123') AS line
FROM PRD_DB_INTEGRATION.INT_KARYAWAN.INT_MPE WHERE LOCATION IN ('2121','2123','2124') AND BULAN BETWEEN '2025-12-31' AND '2026-10-31'
GROUP BY BULAN, EMPL_CLASS ORDER BY BULAN, EMPL_CLASS;
-- 3) Ha tanam per BA (TM + TBM), bulan realisasi terakhir (Sep 2026). Oktober = proyeksi (HEKTAR_PANEN kosong, TM Sekernan loncat 2.744 -> 3.194), jangan dipakai.
SELECT KODE_BA, MATURITY_STATUS, ROUND(SUM(HEKTAR),1) ha FROM PRD_DB_INTEGRATION.INT_PANEN.INT_HEKTAR_BLOK
WHERE KODE_BA IN ('2121','2123','2124') AND DATE_TRUNC('MONTH',BULAN)='2026-09-01' AND MATURITY_STATUS IN ('TM','TBM 3') GROUP BY ALL ORDER BY 1,2;
