# Usage: python3 an_load.py work/r_main.json work/ec_mon.txt work/r_an.json
# Tab Analisa Rp/Kg: BA-level dari ec_mon.txt (hasil query ESTATE_COST per BA per bulan, Rp juta; kolom: ba bln 7 aktual 7 budget ton tonb),
# afdeling dari r_main.json periode Y (Rp ribu). PMY = afd A + C (afd B dibuang). Komponen: Rawat, Infra, Pupuk, Panen, Transport, Umum, Penyusutan.
import sys,json,collections
main=json.load(open(sys.argv[1]));mon=[l.split() for l in open(sys.argv[2]) if l.strip()]
ba={};mm=collections.defaultdict(list)
for r in mon:
    b=r[0];v=[float(x) for x in r[2:]]
    o=ba.setdefault(b,{'T':0,'Tb':0,'a':[0]*7,'b':[0]*7})
    o['T']+=v[14];o['Tb']+=v[15]
    for i in range(7):o['a'][i]+=v[i];o['b'][i]+=v[7+i]
    mm[b].append([int(r[1]),v[14],v[15],sum(v[:7]),sum(v[7:14])])
afd={}
for r in main:
    if r[2]!='Y' or (r[0]=='2131' and r[1]=='B'):continue
    k=(r[0],'PMY' if r[0]=='2131' else r[1])
    o=afd.setdefault(k,{'T':0,'Tb':0,'a':[0]*7,'b':[0]*7})
    o['T']+=float(r[3]);o['Tb']+=float(r[7])
    for i in range(7):o['a'][i]+=float(r[11+i])/1e3;o['b'][i]+=float(r[18+i])/1e3
rd=lambda L:[round(x,1) for x in L]
out={'m':max(x[0] for x in mm['2121']),'src':'PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST (biaya, budget, ton)',
 'ba':{b:{'T':round(o['T'],1),'Tb':round(o['Tb'],1),'a':rd(o['a']),'b':rd(o['b'])} for b,o in ba.items()},
 'afd':[[k[0],k[1],round(o['T'],1),round(o['Tb'],1),rd(o['a']),rd(o['b'])] for k,o in afd.items()],
 'mon':{b:[[x[0],round(x[1],1),round(x[2],1),round(x[3],1),round(x[4],1)] for x in v] for b,v in mm.items()}}
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False,separators=(',',':'))
for b,o in out['ba'].items():
    s=[x for x in out['afd'] if x[0]==b]
    print(b,'ton',o['T'],'vs afd',round(sum(x[2] for x in s),1),'| biaya',round(sum(o['a'])),'vs afd',round(sum(sum(x[4]) for x in s)),'| budget',round(sum(o['b'])),'vs afd',round(sum(sum(x[5]) for x in s)))
