# Memuat hasil q_rawat_cause.sql (Snowflake, satu string 'ba|L1|L2|aktual|budget|unbudgeted|over|under' per baris, ribu Rp YTD) -> <wd>/r_rawcause.json.
# Pakai: python3 rawcause_load.py w10   (membaca w10/rawcause.txt). Tie-out: aktual total harus sama dengan Perawatan Level 1 di r_rawat.json.
import json,sys,os
wd=sys.argv[1] if len(sys.argv)>1 else 'work'
R=[]
for l in open(os.path.join(wd,'rawcause.txt'),encoding='utf-8').read().strip().split("\n"):
    p=l.split("|");R.append([p[0],p[1],p[2]]+[int(x) for x in p[3:]])
a=sum(r[3] for r in R);b=sum(r[4] for r in R);u=sum(r[5] for r in R);o=sum(r[6] for r in R);d=sum(r[7] for r in R)
print(len(R),'aktual',a,'budget',b,'selisih',a-b,'unb',u,'over',o,'under',d,'unb+over-under',u+o-d)
assert abs((a-b)-(u+o-d))<=len(R),'identitas selisih gagal'
json.dump(R,open(os.path.join(wd,'r_rawcause.json'),'w'),separators=(',',':'))
