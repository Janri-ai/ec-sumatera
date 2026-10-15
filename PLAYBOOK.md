# Playbook: update laporan EC Region Sumatera

Permintaan user: "update laporan EC Sumatera sampai YTD <bulan> <tahun>". Hasil: artifact web (URL tetap sama bila republish dengan file path yang sama).
Cakupan: BA 2121 SEK, 2124 SBR, 2131 PMY (2132 dan 2133 dikecualikan). Sumber BIAYA, BUDGET, TON dan HA TM: HANYA tabel PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST (instruksi user 2026-10-07: "semua data estate cost baca dari PRS_COST.ESTATE_COST, jangan ke data lain"). Data non-biaya (ha panen, HK, ton blok TM, pupuk kg, pokok) tetap dari PRD_DB_INTEGRATION. Tool: Snowflake sql_exec_tool.

## Langkah
1. `python3 gen_sql.py YEAR END_MONTH work` -> q_main.sql, q_tm.sql, q_mon.sql, q_pup.sql, q_lang.sql.
2. Jalankan tiap file dengan tool Snowflake. Simpan array `data` hasilnya ke work/r_main.json, r_tm.json, r_mon.json, r_pup.json, r_lang.json, r_pok.json (q_pok.sql). r_tm.json = 5 kolom (ba, afd, p, hapan, tontm). parse_budget.py, q_budba, bud_afd.json dan r_budba.json sudah PENSIUN (budget kini dari ESTATE_COST) (angka boleh dibulatkan; NULL jadi null).
3. `python3 build.py YEAR END_MONTH work work/new.html` (cek baris tie-out: selisih afd-sum vs bulanan harus ~0).
4. `python3 smoke.py work/new.html work/shots` (tidak boleh ada console error / overflow). Lihat screenshot.
5. Bandingkan dengan versi terbit sebelumnya (selisih harus bisa dijelaskan, mis. revisi data sumber), lalu publish ke artifact yang sama (file path sama, tanpa icon baru).
6. Laporkan ke user: ringkasan hasil, perubahan vs versi lama, dan asumsi di bawah.

## Aturan bisnis (sudah disetujui user, jangan diubah tanpa izin)
- BA 2122 = kode lama 2131 (DECODE). Pemayung diberi nama afd "PMY" = afd A + afd C 2131; afd B dikeluarkan sepenuhnya (ton, biaya, budget). Budget ton PMY 4.212 = punya user.
- Luas pembagi Rp/Ha = HA_ACTUAL (TM) dan HA_BUDGET di ESTATE_COST; pembilang = SEMUA biaya (ESTATE_COST tidak punya status TM/TBM, sehingga penurunan biaya TM-only dari INT_COST_ALOKASI dihentikan sesuai instruksi sumber tunggal). Rp/Kg memakai semua biaya dan semua ton.
- Yield TM = ton dari blok TM / ha TM; Yield ha panen = semua ton / ha panen.
- EC total = upkeep + infra + pupuk + panen + transport + OVH + penyusutan. Empat sudut pandang: total; tanpa pupuk; tanpa pupuk+infra; tanpa pupuk+infra+penyusutan.
- Kolom TON_*, HA_* di ESTATE_COST berulang di setiap baris biaya: ambil MAX per (BA, afd, bulan), JANGAN SUM. Kategori dari GROUP_LEVEL: BIAYA PERAWATAN=up, BIAYA INFRA, BIAYA PEMUPUKAN, BIAYA PANEN, TRANSPORT PANEN, BIAYA UMUM+COST SEWA AMP=OVH, BIAYA PENYUSUTAN. Langsir = LEVEL_1 'LANGSIR'.
- BBC = YTD_TON_BBC baris panen terakhir tiap blok sampai akhir bulan (dibawa maju, dijumlah per afd; bulan = selisih akhir bulan) di q_main kolom bbc. Jangan jumlahkan TON_BBC harian (±22% produksi) dan jangan jumlahkan MTD_TON_BBC baris terakhir (±11% terlalu kecil). BBC MTD (periode M) memakai file 'Tarikan BBC ... Detail Blok.xlsx' via bbc_file.py (r_bbcfile.json; hanya 3 bulan terakhir; cocok dengan laporan pemilik). YTD tetap perkiraan Snowflake. Belum identik dengan laporan BBC pemilik untuk YTD (YTD Sep: SEK 41.973 vs 42.557, SBR 30.012 vs 31.452, PMY 3.437 vs 3.512); sumber persisnya belum diketahui. Tab Produktivitas pemanen memakai r_pan.json (gen_sql_panen.py), bukan bagian q_main. VRA Rp/KM, KM langsir, RKB vs PDB belum tersedia di Snowflake.

## Asumsi yang HARUS diungkap ke user setiap update
1. Biaya, budget, ton dan luas TM per afd langsung dari ESTATE_COST (tanpa alokasi, tanpa file budget). PMY: seluruh budget BA ada di afd A dan C; afd B tanpa budget biaya.
2. Rp/Ha = seluruh biaya / luas TM (tidak lagi biaya TM-only), sehingga Rp/Ha di afdeling dengan banyak TBM (SBR B, C, E) lebih tinggi; Rp/Kg tidak terpengaruh.
3. Biaya bulan terakhir sering belum lengkap (penyusutan Rp 0, OVH hampir nol); build.py mendeteksinya otomatis dan menampilkan banner + garis putus-putus. Sarankan pembanding "YTD sampai bulan sebelumnya".
4. Data sumber Snowflake bisa direvisi mundur (contoh: SBR afd C Juli 2026 -26,0 ton) -> selalu tarik ulang penuh, jangan menambah bulan ke data lama.
5. Catatan statis di template (bagian "Belum tersedia dan catatan data") menyebut SBR afd B/C/E didominasi TBM dan biaya afd B PMY (±Rp 5 juta); periksa apakah masih berlaku saat update.

## Struktur data
R = [ba,afd,periode(Y=YTD,M=bulan terakhir,A=YTD s.d. bulan sebelumnya),ton,bbc,ha panen,HK,ton budget,HK budget,ha,ha budget,act[7],bud[7]] (biaya Rp ribu); MON, PUP, LANG, TMD, ADJ: lihat komentar di data.js hasil build. Template: template.html (token {{...}} diisi build.py).

## Pupuk: hanya blok TM
Tabel pupuk hanya menghitung aplikasi di blok TM: aktual = STATUS_MATURITY='TM', rekomendasi = STATUS 'TM (Makro/Mikro)'. r_pup.json punya 8 kolom (ba, afd, jenis, tgt_tm, act_tm, tgt_nontm, act_nontm, tgt_fy). tgt_fy = rekomendasi TM 1 tahun penuh Jan–Des; kolom lain YTD. Volume non-TM (TBM 2/3 dan baris tanpa status) ditampilkan sebagai catatan (PUPX) dan tidak masuk tabel.

## Dosis pupuk
Tabel dosis (kg/Ha TM dan gram/pokok TM) memakai r_pok.json (q_pok: ba, afd, ha_ytd, pokok_ytd, ha_fy, pokok_fy = rata-rata bulanan luas/pokok TM YTD dan setahun; PMY = A + C). Simpan hasil q_pok.sql ke work/r_pok.json. Dosis = kumulatif YTD, bukan per putaran.
Rekomendasi pupuk selalu 1 tahun penuh (aktual YTD). Dosis rekomendasi dibagi luas/pokok TM rata-rata setahun, dosis aktual dibagi rata-rata YTD.

## Tab Hectare Statement (tab pertama)
- Sumber: INT_HEKTAR_BLOK per blok, posisi AKHIR bulan laporan (q_hs di gen_sql.py -> work/r_hs.json, baris: ba, afd, thn, ms, kt, ha, pokok, nblok). Luas tertanam = KATEGORI_TANAH 'PLANTED'; selain itu "tidak ditanam". Status: TBM 0-3 dan TM dari MATURITY_STATUS. SPH = pokok / luas tertanam.
- PMY = afd A + C (BA 2131 dan 2122), afd B dibuang di build.py. Ha TM di laporan EC (rata-rata YTD) cocok dengan HS ini; posisi akhir bulan bisa berbeda bila ada perubahan status di tengah tahun (SBR afd B, C, D berubah pada Juli).

## Ha TM (pembagi Rp/Ha dan yield TM) = Hectare Statement
- Atas permintaan owner, Ha TM aktual di tab Estate Cost dan Laporan produksi diambil dari HS (INT_HEKTAR_BLOK, PLANTED + MATURITY_STATUS TM*) posisi AKHIR bulan terakhir periode (Y dan M: bulan n; A: bulan n-1), bukan rata-rata HA_ACTUAL. q_hstm di gen_sql.py -> work/r_hstm.json (ba, afd, m, ha); build.py mengisi TMD[0]. PMY = afd A + C.
- Luas budget (pembagi TGT) tetap dari ESTATE_COST. Ini pengecualian dari aturan "ha dari ESTATE_COST" hanya untuk Ha TM aktual.
- Konsekuensi: YTD memakai luas posisi akhir; bila TM berubah di tengah tahun (SBR B, C, D pada Juli) Rp/Ha YTD tidak sebanding dengan biaya Jan..n.
- Budget per Ha (TGT Rp/Ha) juga dibagi Ha TM aktual HS yang sama (bukan luas budget ESTATE_COST); ACHV Rp/Ha = biaya aktual / biaya budget.
- (menggantikan butir sebelumnya soal TGT) Budget Ha TM (pembagi TGT Rp/Ha) dari file RKT 2026 "REKAP HECTARE STATEMENT" di folder EC PROJECT CONTOH/HS 2026 (SEKERNAN, PEMAYUNG, BRAHMA SAWIT): `python3 hs_budget.py work/r_hsbgt.json <3 file>` (SBR pakai ..._files/sheet001.htm karena .xls-nya frameset). Kolom TM: SMS 1 untuk periode sampai Juni, SMS 2 sesudahnya. Hasil sama dengan luas budget ESTATE_COST (SEK 2.634, SBR 1.401, PMY 250,4), jadi tidak ada beda angka dibanding sebelumnya. Header file PMY dan SEK tertulis "SMS 1 2027" (salah ketik; isi RKT 2026).

## Produksi per status dan tahun tanam (tab Laporan produksi)
- q_ptt di gen_sql.py -> work/r_ptt.json (baris: ba, afd, thn, ms, ton_a [bulan < n], ton_m [bulan n], hp_a [jumlah ha panen bulanan < n], hp_m). Produksi = SUM(TON_AKTUAL) per blok-bulan, digabung dengan INT_HEKTAR_BLOK blok-bulan yang sama (tahun tanam dan MATURITY_STATUS). Periode Y: ton a+m, ha panen (hp_a+hp_m)/n; A: ton a, ha hp_a/(n-1); M: m.
- Tie-out wajib: jumlah ton per BA = ton ESTATE_COST (SEK 41.900,9, SBR 32.385,8, PMY 3.814,5). PMY = afd A + C, afd B dibuang di build.py. Status per bulan: satu blok yang berganti status di tengah tahun muncul di dua baris status.
- Tabel produksi per status: Ha TM dan Ha TBM (TBM 2+3) dari HS (r_hs.json untuk periode Y dan M; r_hs0.json = HS bulan n-1, hanya baris PLANTED, untuk periode A; q_hs0 di gen_sql.py). Yield ha panen = ton total / ha panen; Yield TM ONLY = ton TM / Ha TM; Yield TBM = ton TBM / Ha TBM; Yield (t/ha TM) = ton total / Ha TM. Produksi memakai status bulan panen, ha memakai status akhir periode, sehingga yield TBM/TM menyimpang bila blok pindah status (SBR afd D).
- (menggantikan butir Ha TM/TBM sebelumnya untuk tabel produksi per status) Ha TM dan Ha TBM (TBM 2+3) = rata-rata hektar bulanan per status dari HS: q_hsavg di gen_sql.py -> work/r_hsavg.json (ba, afd, thn, kind TM/TBM/X, ha_a = jumlah ha bulan < n, ha_m = bulan n). Y = (ha_a+ha_m)/n, A = ha_a/(n-1), M = ha_m. Status ha dan status produksi sama per bulan. r_hs0.json/q_hs0 tidak lagi dipakai. Catatan: Luas TM di tabel atas (Laporan produksi dan Estate Cost) tetap posisi akhir bulan HS, jadi Yield TM ONLY SBR B, C, D berbeda antara tabel atas dan tabel status.

## Budget & BBC per tahun tanam (alokasi proporsional)
Sumber budget produksi hanya ada di ESTATE_COST per afd (ton), BBC per afd/BA; tidak ada sumber per tahun tanam. Baris tahun tanam di tabel produksi = alokasi: angka afd × porsi blok.
- Porsi budget: target ton harian per blok (INT_PANEN_HARIAN_TARGET) dijumlah per afd × tahun tanam (q_alloc.sql #1; blok tanpa tahun tanam di HS tidak ikut). Cocok ke ESTATE_COST: SEK persis, SBR A/E persis, SBR B/D selisih blok '?' (±40/271 t), SBR C ±353 t, PMY A+C 4.253 vs 4.212.
- Porsi BBC: Jan–Jun = YTD_TON_BBC terakhir per blok (q_alloc.sql #2); Jul–Sep = file SAP via `alloc_file.py FILE.xlsx 9 work/r_allocfile.json` (TAHUN TANAM kosong di bulan 2–3 diisi dari blok yang sama). Total file cocok 4.997/3.817/373.
- Hasil query ditulis ke work/r_alloc.json (kolom: ba,afd,thn,kind,tgt_a,tgt_m,bbc_h1,0,0,0). build.py → token __ALC__; template ptt() skala ke angka afd (PMY digabung A+C) sehingga jumlah baris = subtotal (cek: Playwright, selisih hanya pembulatan).

## Budget produksi per blok (file perencanaan produksi) — menggantikan tonB ESTATE_COST
Folder `BUDGET 2026 per AFD/PRODUKSI PER BLOK` berisi ekspor sistem perencanaan: `*_data_perencanaan_produksi_*.xls` (HTML; BUDGET TON.1 final + DISTRIBUSI JAN..DES) dan `*_template_upload_*.csv` (hanya master blok, tahun tanam). Template CSV kosong tidak berisi budget; pakai ekspor "data".
- `python3 budget_blok.py FOLDER work 9` → work/r_bgtblok.json + r_bgtthn.json. build.py menimpa tonB (kolom R[7]) per afd/periode dari r_bgtblok.json, dan memakai r_bgtthn.json sebagai bobot baris tahun tanam (faktor skala = 1 karena total afd sama).
- Tie-out: total per BA = ESTATE_COST (SEK 44.989,3; SBR 33.700,5; PMY 4.211,6). SEK dan SBR A/E persis per afd; SBR B/C/D beda dari ESTATE_COST (+38/+699/−737) karena blok SBR D 133,134,700–703,706 dan SBR C 090 tidak ada di file budget.
- Blok tanpa tahun tanam di HS tampil di baris "Blok tanpa data HS" (SBR B 246 t, SBR D 2.098 t, PMY A 57 t YTD Sep).
- BBC per tahun tanam tetap alokasi proporsional (lihat bagian sebelumnya).

## Progeni di Hectare Statement
INT_HEKTAR_BLOK punya kolom BIBIT (progeni). q_hs sekarang membawa bibit (kolom ke-9; group by BIBIT); build.py menyimpan bibit sebagai HS[8] (underscore diganti spasi). Tabel HS per afd×tahun tanam dan per tahun tanam menampilkan sub-baris "↳ progeni" di bawah tiap tahun tanam (urut luas terbesar). Cek: jumlah luas progeni = baris tahun tanam. Catatan: file perencanaan produksi per blok juga punya JENIS BIBIT (untuk blok di folder PRODUKSI PER BLOK).

## Produksi per progeni (tab Laporan produksi)
Sub-baris "↳ progeni" di bawah tiap tahun tanam pada tabel afd×tahun tanam dan per tahun tanam. Progeni = BIBIT dominan blok (HEKTAR terbesar pada bulan terakhir yang ada; q_ptt_pg dan q_hsavg_pg di gen_sql.py → work/r_ptt_pg.json dan r_hsavg_pg.json; build.py memakainya bila ada, kolom progeni di akhir). Per Sep 2026 tidak ada blok dengan >1 progeni. Budget/BBC tidak dipecah per progeni (kosong). Tie-out: ton 78.101,25 dan ha rata-rata sama dengan versi tanpa progeni.

## Pencapaian produksi terhadap Profile dan Potensi (basis YIELD, t/ha)
Tabel #pS4 (tab Laporan produksi), struktur Estate–Afdeling–Tahun tanam + Subtotal afd/TOTAL; hanya ukuran yield (tidak ada kolom ton produksi). `budget_blok.py` → work/r_pp.json = [ba,afd,thn, profile ton, potensi ton, ha blok berprofil, ha blok berpotensi] (ha = rata-rata SMS1/SMS2 HA; PMY = afd A + C; token __PP__).
- Yield aktual = produksi ÷ Ha tertanam (TM+TBM2/3, rata-rata bulanan HS periode).
- Yield Profile/Potensi setahun = Σ ton ÷ Σ ha blok dengan nilai > 0. Periode = setahun × proporsi (Y: n/12, A: (n−1)/12, M: 1/12), linear tanpa musiman. Ach = yield aktual ÷ yield periode.
- Kolom: Ha tertanam, Yield aktual, Yield Profile setahun/periode, Ach. Profile, Yield Potensi setahun/periode, Ach. Potensi. Nilai 0 ditampilkan "–".
- Yield YTD Sep (setahun): Profile ≈ SEK 21,8 / SBR 19,5 / PMY 27,2; Potensi ≈ 20,7 / 19,1 / 23,2.
- Caveat: blok tidak ada di file (SBR D 133,134,700–703,706; SBR C 090) dan TBM muda berprofil 0 → Ach. SBR B/C terlalu tinggi; penyebut ha aktual (HS) ≠ ha file.

## Tab Summary (di sebelah Hectare Statement)
Level estate saja (SEK, SBR, PMY + Region). Data: token `__SUMM__` = {ba: {ton[n], bbc[n], tgt[n], act[7][n], bud[7][n]}} dibangun di build.py (blok "SUMMARY") dari: ton aktual = MON (r_mon.json); BBC bulanan = Jan..(bulan pertama file SAP −1) selisih kumulatif Snowflake × kalibrasi owner, bulan berikut dari file SAP (jumlahnya = BBC Y di tab Laporan produksi); Target = budget produksi per blok dari file perencanaan, DISTRIBUSI per bulan (r_bgtblok.json); cost 7 komponen aktual+budget per bulan dari `q_sumcost.sql` → work/r_sumcost.json (ribu Rp; tie ke MON per BA). Build mencetak cek "SUMM ... vs R" (ton/BBC/target harus sama dengan baris Y).
- Rp/Kg = biaya (ribu Rp) ÷ ton. Budget Rp/Kg = budget biaya ÷ Target ton (file), sama dengan konvensi tab Estate Cost. Ach cost = aktual ÷ budget (di bawah 100% = hemat); Ach produksi = produksi ÷ BBC atau Target.
- Isi tab: KPI Region, tabel + grafik Ach YTD dan per bulan, grafik produksi/BBC/target bulanan, tabel + grafik EC Rp/Kg (YTD dan bulanan), breakdown 7 komponen per estate, grafik komposisi (stacked A vs B), tabel Rp/Kg per komponen per bulan (kolom Act berwarna vs Bgt) dan tabel Rp ribu/Ha TM dengan struktur sama (Ha TM bulanan = Hectare Statement r_hstm.json, budget = r_hsbgt.json; YTD = biaya kumulatif ÷ Ha TM bulan terakhir, sama dengan tab Estate Cost). SUMM juga membawa ha[n], hab[n]. Filter cakupan hanya memengaruhi grafik/tabel bulanan. Warna komponen: --c1..--c7 (palet kategorikal tervalidasi; wajib legenda + tabel).
- Query cost hanya perlu dijalankan ulang tiap bulan laporan (ganti batas BULAN di q_sumcost.sql).

### Summary: pemupukan dan pemanen (level estate)
- Pemupukan per jenis: dari PUP (build.py, [jenis, rek YTD kg, aktual YTD kg, rek 1 tahun]) hanya blok TM; kolom per estate Rek. YTD, Aktual YTD, Aktual/rek; baris Subtotal NPK dan Total. Grafik batang Aktual/rek per jenis (NPK digabung) per estate; jenis tanpa rekomendasi ditandai "tanpa rek." Hanya YTD (tidak ada data bulanan pupuk). Catatan: NPK 12-12-17-2 / 15-15-6-4 tidak punya rekomendasi sendiri, baca lewat Subtotal NPK.
- Produktivitas pemanen: token `__PANEN__` dipakai ulang di blok Summary (D per ba+afd: [bulan, ton, tonB, HK, HKB, ha, pemanen-hari, tdk basis, ...kelas A/B/C]); Kg/HK = ton×1000/HK, % tdk dapat basis = idx7/idx6, % kelas C = idx12/idx6. Tabel YTD per estate + tabel/grafik bulanan mengikuti filter cakupan. Titik merah bila tdk basis / kelas C > 10%.

- Peringkat afdeling (rank-sum) dipindah dari tab Estate Cost ke tab Summary (bagian paling bawah); selalu YTD dan seluruh Region (R periode Y), tidak mengikuti filter cakupan/periode. Warna baris soft: peringkat 1–2 hijau, 3–5 kuning, 6+ merah (class g/y/r di #tRank). Ringkasan (KPI) Summary mengikuti tombol cakupan.

## Correlation chart Rp/Kg vs Yield (tab Summary, sebelum Peringkat afdeling)
- Clone dari pbix "COST REVIEW & CAPEX 2026_new" (folder EC PROJECT CONTOH), scatter X = yield, Y = Rp/Kg; garis kuning USTP dan hijau TAPG = anchor (jangan dihapus).
- Anchor: `anchor.py` membaca pickle pbix (pbixray) -> work/r_anchor.json (Jan–Jul 2026, TAPG = 28 BA). Anchor TIDAK ikut update bulan; ganti hanya bila user memberi pbix baru. Yield = SUM(Kg)/rata2 Ha TM bulanan/1000; Rp/Kg = SUM(Rp)/SUM(Kg).
- Basis cost = 5 komponen (Rawat, Pupuk, Panen, Transport, Umum; TANPA Infra dan Penyusutan) karena pbix tidak punya Infra/Penyusutan. Query `q_corr.sql` -> work/r_corr.json (key "BAAFD": c5 ribu Rp, ton per bulan; baris nol dibuang; PMY afd B dikeluarkan). Ha TM per afd dari r_hstm.json. Tie-out dicetak build ("CORR ... vs SUMM").
- Validasi: yield YTD Jul ours = pbix persis (SEK 11,47; SBR 16,83; PMY 11,24); Rp/Kg ours 1,5–2,5% lebih rendah dari pbix (selisih klasifikasi komponen).
- Toggle periode: YTD Jul (sama dengan anchor, default) dan YTD bulan laporan (diberi peringatan: yield ikut naik karena puncak produksi). Afdeling Ha TM < 100 tidak digambar. Tren OLS hanya di chart afdeling (R² ditampilkan di legenda).
- Token build: `__CORR__` (build.py blok CORRELATION CHART).

### Revisi Correlation chart: yield TM only (2026-10-08)
- Sumbu X = yield TM = ton blok TM / Ha TM (ton dari `q_corrtm.sql` -> work/r_corrtm.json, tie-out ke r_tm.json Y). Alasan: SBR-B/C/E didominasi TBM (SBR-C hanya 35% ton dari blok TM; Ha TM SBR-C 73,5 Jan–Jun lalu 148,7 mulai Jul), yield ton-total/Ha-TM tidak masuk akal (45-66 t/Ha).
- Filter Ha TM >= 100 DIHAPUS (permintaan user); afd tanpa Ha TM atau ton TM (SBR-E) tidak bisa digambar. Titik EC5 > 3.500 Rp/Kg ditempel di tepi atas (SEK-F) dan tidak ikut tren.
- Rp/Kg tetap biaya 5 komponen / ton TOTAL (biaya ESTATE_COST tidak terpisah TM/TBM) -> SBR-B/C terlihat murah. Anchor pbix = ton total / Ha TM (beda basis, dicatat di halaman).
- PMY afd A dan C diambil dari r_hstm.json asli (hstm di build.py menggabung PMY).

## Tab Estate Cost: klasifikasi kelompok biaya (2026-10-08)
- Rp/Kg (selector `sVK`, st.vk): Total | Tanpa pupuk & penyusutan (komponen 0,1,3,4,5). Rp/Ha (selector `sVH`, st.vh): Total | Tanpa pupuk & penyusutan | Rawat only (Upkeep+Infra: 0,1) | Upkeep only (0) | Infra only (1). Indeks komponen: 0 Upkeep,1 Infra,2 Pupuk,3 Panen,4 Transport,5 OVH,6 Penyusutan.
- Dua section terpisah: "EC Rp/Kg" (tEC, tViewsK, grafik batang dan tren) dan "EC Rp/Ha" (tEH, tViewsH). KPI Rp/Kg mengikuti vk. Grafik tren bulanan tetap EC total (MON hanya menyimpan total).
- `met(o,vk,vh)` menghitung kedua basis; `ecs(o)` = EC* peringkat (komponen 0,3,4,5) dan tidak ikut selector. Pilihan lama "tanpa pupuk & infra" dan "tanpa pupuk, infra & susut" dihapus dari tab Estate Cost.

## Tren produksi + outlook Okt–Des (tab Laporan produksi)
Section "Tren produksi dan outlook s.d. Desember per afdeling" (token `__TREND__`, id tnSec). Jan..n = aktual per afd (r_corr.json ton; PMY = A+C), n+1..12 = BBC outlook = kolom 'Tbs Bulan Ke-2/3/4' sensus terakhir (MONTH max) di file Tarikan BBC, dijumlah per afd (`bbc_file.py` menulis `r_bbcfile_outlook.json`; rename ke work/r_bbcout.json; bulannya harus = bulan laporan). Target = r_bgtblok.json distribusi 12 bulan. Tabel bulanan per afd, rekap Q1–Q4 (basis Aktual/BBC per kuartal otomatis menurut n), grafik batang aktual/outlook + garis target (klik baris = ganti entitas). Tie-out dicetak build ("TREND ... vs MON"). Catatan: BBC bulanan bias (Sep: BBC 4.997 vs aktual 5.640 di SEK); YTD BBC lebih dekat ke aktual.

## Aturan cakupan (semua tab)
Detail semua estate dan afdeling hanya tampil saat tombol Region aktif; memilih SEK/SBR/PMY menampilkan hanya estate itu (baris Region total disembunyikan). Berlaku untuk: tab Summary (smSc mengatur semua tabel dan grafik estate, correlation chart, dan tabel peringkat lewat window.SMSC + rankRedraw; peringkat tetap global), Produksi (tnSc memengaruhi tnT1/tnT2), Estate Cost (tMat, tLang), Produktivitas pemanen (pnTb). Audit dengan work/audit.py (daftar baris tiap tabel saat scope SEK).

## AKP di tab Produktivitas pemanen
Baris AKP di bawah Ha/HK pada grafik Kg/HK. Rumus (dari pemilik laporan, revisi) = jumlah janjang ÷ jumlah pokok ÷ rotasi dalam sebulan. Rotasi tidak ada di Snowflake: diturunkan = HA_PANEN blok TM (jumlah harian) ÷ Ha TM bulan itu (baris "Rotasi" ditampilkan di bawah AKP; ganti bila ada sumber rotasi resmi). Janjang & pokok: janjang = JJG_AKTUAL blok TM (status TM+PLANTED pada bulan panen), pokok = JML_POKOK blok TM bulan itu (INT_HEKTAR_BLOK). Query `q_akp.sql` → work/r_akp.json {"BAAFD":{"jjg":[n],"pk":[n]}} → token `__AKP__` (build.py). Ditampilkan sebagai % (= janjang per pokok per rotasi × 100, ≈20–50%), bukan % harian seperti AKP sensus. r_akp.json juga memuat hap dan ha (untuk rotasi). Afd tanpa TM (SEK-E, SBR-E/H/I/J) tidak dimuat.

## Tab Perawatan (token __RW__, tabRW)
Cost Level 1 BIAYA PERAWATAN (11 item) dan BIAYA INFRA (9 item) dari ESTATE_COST kolom LEVEL_1. `q_rawat.sql` (ganti '2026-09-01' dan batas bulan) → salin kolom JSON per afd ke `rawat_load.py` → work/r_rawat.json; build.py menyisipkan {m:n,d:...}. Per afd: c[20]=[Rp akt YTD, bud YTD, akt bulan, bud bulan] (ribu Rp), ha=[HA_ACTUAL, HA_BUDGET bulan terakhir], ton=[akt YTD, bud YTD, akt bln, bud bln]. Ha/ton = MAX per afd per bulan (berulang di tiap baris ESTATE_COST). Afd tanpa biaya dan ton dibuang (SEK E, I; SBR H–K). Tie-out Sep: total per BA per grup cocok ke ESTATE_COST (selisih ≤5 ribu karena pembulatan) dan ton/ha cocok (SEK 41.900,8 / 2.743,74 dst.). Tampilan: KPI konteks (Ha, output, Rp, Rp/Ha), tabel non-infra, tabel infra, tabel per estate/afd; ikut tombol Periode (YTD/bulan) dan Cakupan; Region menampilkan semua estate dan afd.
- Output perawatan (Ha dikerjakan ÷ HK bekerja): `q_rawat_out.sql` → salin ke `rawout_load.py` → work/r_rawout.json (build.py: RWJ.o). Ha dari INT_RAWAT_HARIAN (UOM=HA, aktivitas TM/TBM, tanpa pupuk), HK = NIK×tanggal berbeda, Ha RKT = INT_RAWAT_TARGET.QTY_TARGET (kode aktivitas ber-UOM Ha). Pemetaan aktivitas→Level 1: nama dinormalkan vs LEVEL_2 ESTATE_COST + tabel manual mp di SQL. Hanya 6 Level 1 punya output Ha/HK; infra praktis kosong (kecuali Konservasi Tanah). Ha/HK budget tidak ada (tidak ada HK budget perawatan). Cakupan Ha RKT tidak merata (SBR B jauh di bawah aktual); Tunasan Ha sering 0 padahal HK ada.
- HK/Ha vs norma (tabel non-infra, v80): `q_rawat_norma.sql` → salin ke `rawnorm_load.py` → work/r_rawnorm.json (build.py: RWJ.n). Per afd × Level 1: [Ha, HK, HK norma=ΣHa×norma] YTD & bulan. Norma dari BUDGET GUIDELINES 2025 sheet "VIII - TM" (datar/mineral), hanya aktivitas TM berstatuan Ha; Level 1 tanpa norma tampil "–". Kolom Ha Actual/Ha RKT dihapus dari tampilan (r_rawout.json tidak lagi dipakai di tabel).

## Tab baru (v82–v90)
- Pemupukan (PU): dipindah dari Estate Cost; resume Rp/Ha, kg/pokok, grafik cost element (pupelem_load.py / q_pupelem.sql).
- Gaji & Premi Panen & Transport (PG): dari ESTATE_COST akun Labors/insentif (q_gaji.sql, gaji_load.py); premi = batas bawah; toggle Rp juta / Rp/Kg.
- Cost Element (CE): ESTATE_COST aktual vs budget, level 1=GROUP_LEVEL, 2=LEVEL_1, 3=LEVEL_2, 4=LEVEL_3(COA); hanya baris non-nol; klik baris untuk expand; Rp/Kg pakai ton ESTATE_COST. Token __CE__ di build.py dari work/r_ce.json (q_ce.sql -> ce_load.py). Bulan hard-coded '2026-09-01' di q_ce.sql -> ganti saat update bulan.


## Tab baru (v93-v96)
- **Trend Estate Cost** (di bawah Ringkasan): grafik Rp/Kg dan Rp/Ha per bulan + Yield t/Ha TM (sumbu kedua), tabel tonase. Data dari __SUMM__; fungsi window.ecTrend dipanggil di akhir render() EC.
- **Capex** (`capex_load.py`): `python3 capex_load.py work/capex.xlsx '<tgl update>' work/r_capex.json` -> token __CX__. Dept S21 BBB S=SEK, S24 BBB SK=SBR, S22 BBB P=PMY, S23 BBB K=Karet RSS.
- **Overhead Cost** (`overhead_load.py`, `q_overhead.sql`): TM YTD dari Snowflake, BUKAN file OPEX (file OPEX_0926 hanya angka September, jangan dilabeli YTD). Aktual = PRS_COST.OPEX_BIAYA_UMUM (TM), budget = INT_COST.INT_COST_BUDGET (GROUP_LVL OVERHEAD SITE, TM); tanpa COA 52010119% (depresiasi), 5201010598 (sewa AMP), 5201012001. Jalankan q_overhead.sql, simpan hasil ke work/oh_ytd.txt (BA|COA|aktual ribu|budget ribu), lalu `python3 overhead_load.py work/oh_ytd.txt 'YTD Jan-Sep 2026' work/r_opex.json` (butuh work/coa_map.json: COA -> [grup, deskripsi]). Wajib cocok dgn ESTATE_COST BIAYA UMUM YTD per estate; Sewa AMP (ESTATE_COST COST SEWA AMP) disimpan di X.amp untuk rekonsiliasi ke komponen OVH.


## Head Count (tab HC, antara Overhead dan Capex)
- Sumber HANYA sheet 'FIX Region Kalteng & Sumatera' (file revisi d0843483, layout baru khusus Sumatera). File lama (9f0100c5, kolom BA..CE) salah: kolom plan tidak sejajar, jangan dipakai.
- Loader: `python3 hc_load.py <xlsx> work/r_hc.json`. Kolom: A jabatan; B-H BBB Sekernan & Batang Hari (MPP B, MPE existing C, AFD D, nama E, plan F, nama plan G); I-O BBB Brahma Sawit & Karet (I, J, K, L, M, N); V-AA RO Sumatera (V, W, nama X, plan Y, nama plan Z); AB-AG HPS (x=true, di luar Total Sumatera). RO Kalteng (P-U) tidak dipakai.
- Baris dengan kolom A kosong = lanjutan jabatan di atasnya (nama tambahan). Satu jabatan di banyak baris (Asisten Lapangan per AFD) dijumlahkan. Loader memvalidasi per seksi dan grand total terhadap baris TOTAL (harus 'validasi beda: 0').
- Hasil 14 Sep: Sekernan MPP 36/MPE 35/plan 34; Brahma 31/24/26; RO 1/1/1; Total Sumatera 68/60/61; HPS 6/4/4 (terpisah).
- Varian existing = MPE existing - MPP; varian plan = plan - MPP. 'plasma' -> 'KEMITRAAN'. Tanpa IN/OUT/FPTK. Tanda ⚠ = jumlah nama unik != MPE existing.

## Head Count Non-Staff (tab HN, setelah Head Count Staff)
- Sumber Snowflake `PRD_DB_INTEGRATION.INT_KARYAWAN.INT_MPE` (snapshot akhir bulan, LOCATION = kode BA). Sekernan = 2121; Brahma Sawit & Karet = 2124 + 2123. Query: `q_hcns.sql` (dua query: detail jabatan bulan tampil, status karyawan Des-tahun lalu s/d bulan berjalan). Simpan hasil ke `work/hcns.txt` (format ada di file contoh `hcns_data.txt`), lalu `python3 hcns_load.py work/hcns.txt work/r_hcns.json` (token __HN__ di build.py). Validasi: total detail = total status per bulan.
- JOB_CODE KOSONG di semua baris INT_MPE dan INT_MASTER_KARYAWAN_NON_STAFF_BULANAN: jabatan = JOB_DESCRIPTION, dikelompokkan JOB_TYPE (HV, WD, OT, TP, WS, PD, NR, LC...). Tidak ada MPP/target non-staff di Snowflake: hanya MPE.
- INT_MPE tidak berisi staff untuk BA ini (MGR_LEVEL hanya NS1-NS3 atau kosong). INT_MASTER_KARYAWAN_NON_STAFF_BULANAN adalah subset (~1.830 orang, hanya bulanan) jadi tidak dipakai.
- BULAN setelah bulan berjalan di INT_MPE hanyalah salinan proyeksi (jumlah datar), jangan dipakai. Jumlah status KL (lepas) tidak berubah sejak Des 2025 (2121: 399, 2123: 515, 2124: 0): kemungkinan tidak diperbarui, konfirmasi ke HR.
- Hasil Sep 2026: Sekernan 3.805; Brahma Sawit 1.286 + Karet 1.599 = 2.885; selisih +920. Okt (berjalan): 3.813 vs 2.910, +903.
