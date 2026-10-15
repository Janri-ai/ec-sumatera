# EC Sumatera — Site Operational Report (BA 2121 SEK, 2124 SBR, 2131 PMY)

Web report "Site Operational Report-YTD <bulan> 2026": satu file HTML (template.html + data JSON) dengan tab Hectare Statement, Summary, Produksi, Estate Cost, Produktivitas Pemanen, Perawatan, Pemupukan, Gaji & Premi, Cost Element, Overhead Cost, Head Count Staff, Head Count Non-Staff, HK NS to OH, Capex.

Baca PLAYBOOK.md dulu: sumber data tiap tab, aturan validasi, dan jebakan data (JOB_CODE kosong, bulan setelah bulan laporan adalah proyeksi, dst).

## Alur
1. Jalankan query q_*.sql di Snowflake (MCP Snowflake) → simpan ke work/ (mis. work/hcns.txt, work/oj.txt, work/oh_ytd.txt).
2. Loader per tab ubah hasil query jadi work/r_*.json (hc_load.py, hcns_load.py, oj_load.py, overhead_load.py, gaji_load.py, ...).
3. `python3 build.py 2026 9 work work/newNN.html` (tahun, bulan, folder kerja, output) menyuntikkan JSON ke token __HC__, __HN__, __OJ__, __OH__, __CX__ dst di template.html.
4. `python3 smoke.py work/newNN.html work/smokeNN` (Playwright): harus tanpa error, scrollWidth desktop 1200 / mobile 400.
5. Publikasikan hasil sebagai artifact/HTML. Jangan edit hasil build; edit template.html lalu build ulang.

## Aturan penting
- Head Count Staff: hanya sheet "FIX Region Kalteng & Sumatera"; validasi total harus "validasi beda: 0".
- Head Count Non-Staff: MPE dari Snowflake INT_MPE; gabungkan jabatan sama lintas JOB_TYPE; total 3.805 / 1.286 / 1.599 (Sep 2026).
- HK NS to OH: biaya per jabatan COA 5201010101 dari INT_COST_ALOKASI; tidak persis sama dengan OPEX_BIAYA_UMUM (catatan ada di halaman).
- Overhead Cost harus cocok dengan ESTATE_COST LEVEL_1='BIAYA UMUM' YTD.
- Data sumber (xlsx) tidak disertakan; minta file terbaru dari Janri.
