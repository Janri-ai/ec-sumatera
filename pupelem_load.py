# Hasil q_pupelem.sql -> work/r_pupelem.json ; D[ba][el]=[YTD aktual, YTD budget] ribu Rp. el: M material, L HK/labors, T transport, C kontrak, A alat, X lainnya
import json
D={"2121":{"M":[12222388,14321888],"L":[2813862,3115688],"T":[1996700,742430],"C":[0,0],"A":[0,0],"X":[0,0]},
"2124":{"M":[8996109,11232928],"L":[1211044,1358807],"T":[2583265,1650052],"C":[0,0],"A":[0,0],"X":[0,0]},
"2131":{"M":[1125189,1661492],"L":[109578,136904],"T":[17838,28268],"C":[0,0],"A":[0,0],"X":[0,0]}}
json.dump(D,open('work/r_pupelem.json','w'),separators=(',',':'))
print({k:sum(v[0] for v in d.values()) for k,d in D.items()})
