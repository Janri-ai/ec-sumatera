"""Head Count Non-Staff: python3 hcns_load.py work/hcns.txt work/r_hcns.json
Input: hasil q_hcns.sql (baris 'bln|tipe|jabatan|2121|2124|2123' di bawah '#detail', 'bln|kelas|2121|2124|2123' di bawah '#kelas').
Bagian #ha: luas tanam (TM dan TBM) per BA dari INT_PANEN.INT_HEKTAR_BLOK akhir bulan realisasi (Okt 2026 = proyeksi, HEKTAR_PANEN kosong, jangan dipakai).
Validasi: total detail per bulan harus sama dengan total kelas per bulan."""
import sys,json
src,out=sys.argv[1],sys.argv[2]
sec=None;det={};cls={};ha={}
for l in open(src,encoding='utf-8'):
    l=l.rstrip('\n')
    if l.startswith('#detail'):sec='d';continue
    if l.startswith('#kelas'):sec='k';continue
    if l.startswith('#ha'):sec='h';continue
    if not l.strip():continue
    p=l.split('|')
    if sec=='d':det.setdefault(p[0],[]).append([p[1],p[2],int(p[3]),int(p[4]),int(p[5])])
    elif sec=='h':ha.setdefault(p[0],{})[p[1].lower()]=float(p[2])
    else:cls.setdefault(p[0],{})[p[1]]=[int(p[2]),int(p[3]),int(p[4])]
bad=0
for m,rows in det.items():
    a=[sum(r[2+i] for r in rows) for i in range(3)];b=[sum(v[i] for v in cls[m].values()) for i in range(3)]
    if a!=b:bad+=1;print('BEDA',m,a,b)
json.dump({'src':'Snowflake PRD_DB_INTEGRATION.INT_KARYAWAN.INT_MPE (snapshot akhir bulan)','det':det,'cls':cls,'ha':ha,'haAsof':'akhir Sep 2026'},open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print({m:[sum(r[2+i] for r in rows) for i in range(3)] for m,rows in det.items()},'validasi beda:',bad)
