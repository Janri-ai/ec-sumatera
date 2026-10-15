import re
s=open('template.html').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)>=1,a[:70]
    s=s.replace(a,b,cnt)
rep('let sel="ALL";','let sel="ALL",scp="ALL";const vis=()=>rows.filter(r=>scp==="ALL"||r.id.startsWith(scp));')
rep('"</thead><tbody>"+rows.map(','"</thead><tbody>"+vis().map(',2)
rep('x.setAttribute("aria-pressed",k===sel);x.onclick=()=>{sel=k;draw()}','x.setAttribute("aria-pressed",k===sel);x.onclick=()=>{sel=k;scp=k;draw()}')
rep('const P=R.filter(r=>r[2]==="Y").filter(r=>r[9]>=100&&r[3]>0).map(r=>{const o=mk([r]);return{l:','const SCR=window.SMSC||"ALL";const P=R.filter(r=>r[2]==="Y").filter(r=>r[9]>=100&&r[3]>0).map(r=>{const o=mk([r]);return{b:r[0],l:')
rep('P.map((p,i)=>tr([i+1,p.l,nf(p.ha),pc(p.bbc,0)','P.map((p,i)=>[p,i]).filter(([p])=>SCR==="ALL"||p.b===SCR).map(([p,i])=>tr([i+1,p.l,nf(p.ha),pc(p.bbc,0)')
rep('return{l:r[1]==="PMY"?"PMY":BN[r[0]]+"-"+r[1],o,ha:o.ha','return{b:r[0],l:r[1]==="PMY"?"PMY":BN[r[0]]+"-"+r[1],o,ha:o.ha')
rep('Q.map((p,i)=>tr([i+1,p.l,nf(p.ha),cell(p.ap,p.rap)','Q.map((p,i)=>[p,i]).filter(([p])=>SCR==="ALL"||p.b===SCR).map(([p,i])=>tr([i+1,p.l,nf(p.ha),cell(p.ap,p.rap)')
rep('function rank(){','window.rankRedraw=()=>rank();\nfunction rank(){')
rep('BAS.map(b=>{const t=mk(R.filter(r=>r[0]===b&&r[2]==="Y")).ton;return tr([BN[b]','BAS.filter(b=>st.sc==="ALL"||b===st.sc).map(b=>{const t=mk(R.filter(r=>r[0]===b&&r[2]==="Y")).ton;return tr([BN[b]')
rep(' BAS.forEach(ba=>{const rs=P.filter(r=>r[0]===ba);rs.forEach((r,i)=>{body+=line(i?"":BN[ba],r[1],mk([r]))});body+=line(BN[ba],"TOTAL",mk(rs),"tot")});\n body+=line("Region","TOTAL",mk(P),"tot");',' BAS.filter(ba=>st.sc==="ALL"||ba===st.sc).forEach(ba=>{const rs=P.filter(r=>r[0]===ba);rs.forEach((r,i)=>{body+=line(i?"":BN[ba],r[1],mk([r]))});body+=line(BN[ba],"TOTAL",mk(rs),"tot")});\n if(st.sc==="ALL")body+=line("Region","TOTAL",mk(P),"tot");')
rep(' h+=row("tot","Region Sumatera",agg(ids,st.per));\n for(const ba of Object.keys(BAN)){',' if(st.sc==="ALL")h+=row("tot","Region Sumatera",agg(ids,st.per));\n for(const ba of Object.keys(BAN).filter(b=>st.sc==="ALL"||b===st.sc)){')
rep('const SC=[["ALL","Region"],...bas.map(b=>[b,BN[b]])],ET=SC.map(([k,l])=>({k,l,y:ytd(k)}));\nlet sc="ALL";','const SC=[["ALL","Region"],...bas.map(b=>[b,BN[b]])],ET=SC.map(([k,l])=>({k,l,y:ytd(k)}));\nlet sc="ALL";window.SMSC="ALL";\nconst VE=()=>sc==="ALL"?[...ET.slice(1),ET[0]]:[ET.find(e=>e.k===sc)],VS=()=>sc==="ALL"?[...SC.slice(1),SC[0]]:[SC.find(x=>x[0]===sc)],ETv=()=>sc==="ALL"?ET:[ET.find(e=>e.k===sc)];')
rep(' const ord1=[...ET.slice(1),ET[0]];',' const ord1=VE();')
rep('  [...ET.slice(1),ET[0]].map(e=>tr([e.l,nf(e.y.ton),nf(e.y.A/1000)','  VE().map(e=>tr([e.l,nf(e.y.ton),nf(e.y.A/1000)')
rep(' const ord=[...ET.slice(1),ET[0]];\n let h1=',' const ord=VE();\n let h1=')
rep(' const ord=[...SC.slice(1),SC[0]];\n const cells=',' const ord=VS();\n const cells=')
rep('keys=[...names.filter(x=>!x.startsWith("NPK")),"NPK (semua)","Total"],ests=SC.slice(1);','keys=[...names.filter(x=>!x.startsWith("NPK")),"NPK (semua)","Total"],ests=sc==="ALL"?SC.slice(1):[SC.find(x=>x[0]===sc)],ci=ests.map(([k])=>bas.indexOf(k));')
rep('fill="${cols[k]}"/><text x="${x(q)+6}"','fill="${cols[ci[k]]}"/><text x="${x(q)+6}"')
rep('<i class="sw" style="background:${cols[k]}"></i>${ests[k][1]}: aktual','<i class="sw" style="background:${cols[ci[k]]}"></i>${ests[k][1]}: aktual')
rep('function pemanen(){\n const ord=[...SC.slice(1),SC[0]];','function pemanen(){\n const ord=VS();')
def fix(a_,b_):
    global s
    a=s.index(a_); b=s.index(b_,a)
    s=s[:a]+re.sub(r'\bET\b','ETv()',s[a:b])+s[b:]
fix('function hbars(){','function lines(')
fix('function costBars(){','function stacked(')
fix('function stacked(){','function monthly(')
rep('x.setAttribute("aria-pressed",x===b));monthly()};seg.appendChild(b)});','x.setAttribute("aria-pressed",x===b));window.SMSC=sc;monthly();hbars();costBars();stacked();pupuk();corr();window.rankRedraw&&window.rankRedraw()};seg.appendChild(b)});')
rep('Cakupan grafik bulanan','Cakupan')
rep(' return out}\nfunction trend(P)',' if(sc!=="ALL"){const bn=BN[sc];out.af=out.af.filter(p=>p.l.startsWith(bn+"-"));out.es=out.es.filter(p=>p.l===bn);out.ex=out.ex.filter(l=>l.startsWith(bn+"-"))}\n return out}\nfunction trend(P)')
open('template.html','w').write(s)
