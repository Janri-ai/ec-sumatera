# Hasil q_pupelem.sql -> WORKDIR/r_pupelem.json ; D[ba][el]=[YTD aktual, YTD budget] ribu Rp. el: M material, L HK/labors, T transport, C kontrak, A alat, X lainnya
import json,sys
W=sys.argv[1] if len(sys.argv)>1 else 'work'
D={"2121":{"M":[14503689,17046338],"L":[3138979,3511840],"T":[2388661,817825],"C":[0,0],"A":[0,0],"X":[0,0]},
"2124":{"M":[10795648,13076714],"L":[1359454,1488798],"T":[2899612,1772479],"C":[0,0],"A":[0,0],"X":[0,0]},
"2131":{"M":[1314968,1855458],"L":[118950,145523],"T":[21505,31439],"C":[0,0],"A":[0,0],"X":[0,0]}}
json.dump(D,open(W+'/r_pupelem.json','w'),separators=(',',':'))
print({k:sum(v[0] for v in d.values()) for k,d in D.items()})
