(function(){
const S=__SUMM__,bas=BAS.filter(b=>S[b]),n=S[bas[0]].ton.length;
const MS=["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"].slice(0,n);
const CAT=["Rawat","Infra","Pupuk","Panen","Transport","Umum","Penyusutan"],CC=[1,2,3,4,5,6,7].map(i=>`var(--c${i})`);
const el=id=>document.getElementById(id),z=()=>Array(n).fill(0),sum=a=>a.reduce((x,y)=>x+y,0);
const agg=sc=>{const bs=sc==="ALL"?bas:[sc],o={ton:z(),bbc:z(),tgt:z(),act:CAT.map(z),bud:CAT.map(z)};
 for(const b of bs){const s=S[b];for(let m=0;m<n;m++){o.ton[m]+=s.ton[m];o.bbc[m]+=s.bbc[m];o.tgt[m]+=s.tgt[m];for(let k=0;k<7;k++){o.act[k][m]+=s.act[k][m];o.bud[k][m]+=s.bud[k][m]}}}return o};
const ytd=sc=>{const o=agg(sc),ton=sum(o.ton),tgt=sum(o.tgt),act=o.act.map(sum),bud=o.bud.map(sum),A=sum(act),B=sum(bud);
 return{ton,bbc:sum(o.bbc),tgt,A,B,kgA:A/ton,kgB:B/tgt,ck:act.map(x=>x/ton),bk:bud.map(x=>x/tgt),ca:act,cb:bud}};
const SC=[["ALL","Region"],...bas.map(b=>[b,BN[b]])],ET=SC.map(([k,l])=>({k,l,y:ytd(k)}));
let sc="ALL";
const dv=(a,b)=>b>0?a/b:null;
const ap=r=>r==null?"–":`<span class="dot ${r>=1?"ok":"no"}"></span>${nf(r*100,1)}%`;      // produksi: tinggi = baik
const ac=r=>r==null?"–":`<span class="dot ${r<=1?"ok":"no"}"></span>${nf(r*100,1)}%`;      // cost: rendah = baik
const sg=(v,d=0)=>v==null||!isFinite(v)?"–":(v>0?"+":v<0?"−":"")+nf(Math.abs(v),d);
const nice=(mx,c=4)=>{const r=mx/c,p=Math.pow(10,Math.floor(Math.log10(r))),f=[1,2,2.5,5,10].find(x=>x*p>=r);return f*p};
const tb=(id,h,b)=>{el(id).innerHTML="<thead><tr>"+h.map(x=>`<th>${x}</th>`).join("")+"</tr></thead><tbody>"+b+"</tbody>"};
const tr=(c,cls="")=>`<tr class="${cls}">`+c.map(x=>`<td>${x}</td>`).join("")+"</tr>";
const axisY=(W,L,R,T,H,B,lo,hi,st,fmt)=>{let s="";for(let v=lo;v<=hi+1e-9;v+=st){const y=T+(H-T-B)*(1-(v-lo)/(hi-lo));s+=`<line x1="${L}" x2="${W-R}" y1="${y}" y2="${y}" stroke="var(--grid)"/><text x="${L-6}" y="${y+4}" text-anchor="end">${fmt(v)}</text>`}return s};

function kpis(){const t=ET[0].y;
 const k=[["Produksi YTD "+MS[n-1],nf(t.ton)+" ton","BBC "+nf(t.bbc)+" · Target "+nf(t.tgt)],
 ["Ach. BBC",ap(dv(t.ton,t.bbc)),"selisih "+sg(t.ton-t.bbc)+" ton"],
 ["Ach. Target",ap(dv(t.ton,t.tgt)),"selisih "+sg(t.ton-t.tgt)+" ton"],
 ["EC Rp/Kg aktual",nf(t.kgA),"budget "+nf(t.kgB)+" Rp/Kg"],
 ["Ach. cost (lebih rendah lebih baik)",ac(dv(t.kgA,t.kgB)),"selisih "+sg(t.kgA-t.kgB)+" Rp/Kg"]];
 el("smK").innerHTML=k.map(x=>`<div class="kpi"><div class="l">${x[0]}</div><div class="v">${x[1]}</div><div class="d">${x[2]}</div></div>`).join("");
 el("smEy").textContent="Ringkasan Region Sumatera · YTD Jan–"+MS[n-1];el("smPer").textContent="Tabel dan grafik YTD selalu per estate; grafik bulanan mengikuti cakupan"}

function tables(){
 tb("smT1",["Estate","Produksi (ton)","BBC (ton)","Target (ton)","Ach. BBC","Ach. Target","Selisih vs BBC (ton)","Selisih vs Target (ton)"],
  ET.map(e=>tr([e.l,nf(e.y.ton),nf(e.y.bbc),nf(e.y.tgt),ap(dv(e.y.ton,e.y.bbc)),ap(dv(e.y.ton,e.y.tgt)),sg(e.y.ton-e.y.bbc),sg(e.y.ton-e.y.tgt)],e.k==="ALL"?"tot":"")).reverse().slice(0,3).concat(tr([ET[0].l,nf(ET[0].y.ton),nf(ET[0].y.bbc),nf(ET[0].y.tgt),ap(dv(ET[0].y.ton,ET[0].y.bbc)),ap(dv(ET[0].y.ton,ET[0].y.tgt)),sg(ET[0].y.ton-ET[0].y.bbc),sg(ET[0].y.ton-ET[0].y.tgt)],"tot")).join(""));
 const o=agg(sc),lb=SC.find(x=>x[0]===sc)[1];
 tb("smT2",[lb+" (ton)",...MS,"YTD"],
  tr(["Produksi",...o.ton.map(v=>nf(v)),nf(sum(o.ton))])+tr(["BBC",...o.bbc.map(v=>nf(v)),nf(sum(o.bbc))])+tr(["Target",...o.tgt.map(v=>nf(v)),nf(sum(o.tgt))])+
  tr(["Ach. BBC",...o.ton.map((v,i)=>ap(dv(v,o.bbc[i]))),ap(dv(sum(o.ton),sum(o.bbc)))],"tot")+tr(["Ach. Target",...o.ton.map((v,i)=>ap(dv(v,o.tgt[i]))),ap(dv(sum(o.ton),sum(o.tgt)))],"tot"));
 tb("smT3",["Estate","Produksi (ton)","Biaya aktual (Rp juta)","Biaya budget (Rp juta)","EC aktual (Rp/Kg)","EC budget (Rp/Kg)","Selisih (Rp/Kg)","Ach. cost"],
  [...ET.slice(1),ET[0]].map(e=>tr([e.l,nf(e.y.ton),nf(e.y.A/1000),nf(e.y.B/1000),nf(e.y.kgA),nf(e.y.kgB),sg(e.y.kgA-e.y.kgB),ac(dv(e.y.kgA,e.y.kgB))],e.k==="ALL"?"tot":"")).join(""));
 // breakdown per komponen: kolom per estate
 const ord=[...ET.slice(1),ET[0]];
 let h1='<tr><th rowspan="2">Komponen (Rp/Kg)</th>'+ord.map(e=>`<th colspan="3" class="g">${e.l}</th>`).join("")+"</tr>",h2="<tr>"+ord.map(()=>'<th class="bl">Aktual</th><th>Budget</th><th>Ach.</th>').join("")+"</tr>";
 let b="";CAT.forEach((c,k)=>{b+=tr([`<i class="sw" style="background:${CC[k]}"></i>${c}`,...ord.flatMap(e=>[nf(e.y.ck[k]),nf(e.y.bk[k]),ac(dv(e.y.ck[k],e.y.bk[k]))])])});
 b+=tr(["Total EC",...ord.flatMap(e=>[nf(e.y.kgA),nf(e.y.kgB),ac(dv(e.y.kgA,e.y.kgB))])],"tot");
 el("smT4").innerHTML="<thead>"+h1+h2+"</thead><tbody>"+b+"</tbody>";
 for(const r of el("smT4").querySelectorAll("tbody tr"))[...r.children].forEach((c,i)=>{if(i>0&&(i-1)%3===0)c.classList.add("bl")});
 // heatmap bulan x komponen
 let hb="";CAT.forEach((c,k)=>{hb+="<tr><td><i class=\"sw\" style=\"background:"+CC[k]+"\"></i>"+c+"</td>"+MS.map((m,i)=>{const a=o.act[k][i]/o.ton[i],bu=o.bud[k][i]/o.tgt[i],r=bu>0?a/bu-1:0,w=Math.min(Math.abs(r)/0.5,1)*45,col=bu>0?`color-mix(in srgb,var(${r>0?"--bad":"--good"}) ${w}%,transparent)`:"transparent";
   return `<td style="background:${col}" title="${m}: aktual ${nf(a)} · budget ${nf(bu)} Rp/Kg (${bu>0?sg(r*100,0)+"%":"–"})">${nf(a)}</td>`}).join("");
  const ya=sum(o.act[k])/sum(o.ton),yb=sum(o.bud[k])/sum(o.tgt),yr=yb>0?ya/yb-1:0;hb+=`<td class="bl" style="background:color-mix(in srgb,var(${yr>0?"--bad":"--good"}) ${Math.min(Math.abs(yr)/0.5,1)*45}%,transparent)" title="YTD: aktual ${nf(ya)} · budget ${nf(yb)}">${nf(ya)}</td></tr>`});
 hb+="<tr class=\"tot\"><td>Total EC</td>"+MS.map((m,i)=>`<td title="budget ${nf(sum(o.bud.map(x=>x[i]))/o.tgt[i])}">${nf(sum(o.act.map(x=>x[i]))/o.ton[i])}</td>`).join("")+`<td class="bl">${nf(sum(o.act.map(sum))/sum(o.ton))}</td></tr>`;
 el("smT5").innerHTML="<thead><tr><th>"+lb+" (Rp/Kg)</th>"+MS.map(m=>`<th>${m}</th>`).join("")+'<th class="bl">YTD</th></tr></thead><tbody>'+hb+"</tbody>"}

// ---- grafik ----
function hbars(){const box=el("smC1"),W=520,L=64,R=44,rh=46,H=ET.length*rh+26,T=6;
 const mx=Math.max(1.1,...ET.flatMap(e=>[dv(e.y.ton,e.y.bbc),dv(e.y.ton,e.y.tgt)]))*1.05,x=v=>L+(W-L-R)*v/mx;
 let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Ach YTD terhadap BBC dan Target per estate">`;
 for(let v=0;v<=mx;v+=.25)s+=`<line x1="${x(v)}" x2="${x(v)}" y1="${T}" y2="${H-20}" stroke="var(--grid)"/><text x="${x(v)}" y="${H-6}" text-anchor="middle">${Math.round(v*100)}%</text>`;
 ET.forEach((e,i)=>{const y=T+i*rh,a=dv(e.y.ton,e.y.bbc),b=dv(e.y.ton,e.y.tgt);
  s+=`<g class="h" data-i="${i}"><text x="${L-8}" y="${y+24}" text-anchor="end" style="font-weight:600">${e.l}</text>
  <path d="M${L} ${y+6}h${x(a)-L-4}a4 4 0 0 1 4 4v8a4 4 0 0 1-4 4h-${x(a)-L-4}z" fill="var(--s1)"/><text x="${x(a)+6}" y="${y+20}">${nf(a*100,1)}%</text>
  <path d="M${L} ${y+24}h${x(b)-L-4}a4 4 0 0 1 4 4v8a4 4 0 0 1-4 4h-${x(b)-L-4}z" fill="var(--s2)"/><text x="${x(b)+6}" y="${y+38}">${nf(b*100,1)}%</text><rect x="0" y="${y}" width="${W}" height="${rh}" fill="transparent"/></g>`});
 s+=`<line x1="${x(1)}" x2="${x(1)}" y1="${T}" y2="${H-20}" stroke="var(--ink2)" stroke-dasharray="4 3"/></svg>`;box.innerHTML=s;
 box.querySelectorAll("g.h").forEach(g=>{const e=ET[+g.dataset.i].y;bindTip(box,g,`<b>${ET[+g.dataset.i].l}</b><br>Ach. BBC ${nf(e.ton/e.bbc*100,1)}% (${nf(e.ton)} / ${nf(e.bbc)} ton)<br>Ach. Target ${nf(e.ton/e.tgt*100,1)}% (${nf(e.ton)} / ${nf(e.tgt)} ton)`)})}

function lines(id,ser,o){ // ser: [{c,d(dash),v:[...],n}], o:{ref,fmt,lo,hi,st,lab}
 const box=el(id),W=520,H=240,L=50,R=14,T=14,B=26,N=n,x=i=>L+(W-L-R)*(N===1?.5:i/(N-1)),y=v=>T+(H-T-B)*(1-(v-o.lo)/(o.hi-o.lo));
 let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${o.lab}">`+axisY(W,L,R,T,H,B,o.lo,o.hi,o.st,o.fmt);
 MS.forEach((m,i)=>s+=`<text x="${x(i)}" y="${H-8}" text-anchor="middle">${m}</text>`);
 if(o.ref!=null)s+=`<line x1="${L}" x2="${W-R}" y1="${y(o.ref)}" y2="${y(o.ref)}" stroke="var(--ink2)" stroke-dasharray="4 3"/>`;
 ser.forEach(q=>{s+=`<path d="${q.v.map((v,i)=>(i?"L":"M")+x(i)+" "+y(v)).join("")}" fill="none" stroke="${q.c}" stroke-width="2" ${q.d?'stroke-dasharray="5 3"':""} stroke-linejoin="round"/>`;
  q.v.forEach((v,i)=>s+=`<circle cx="${x(i)}" cy="${y(v)}" r="4" fill="${q.c}" stroke="var(--surf)" stroke-width="2"/>`)});
 s+=`<line class="cr" x1="0" x2="0" y1="${T}" y2="${H-B}" stroke="var(--ref)" visibility="hidden"/>`;
 MS.forEach((m,i)=>s+=`<rect class="hv" data-i="${i}" x="${x(i)-(W-L-R)/(N-1)/2}" y="${T}" width="${(W-L-R)/(N-1)}" height="${H-T-B}" fill="transparent"/>`);
 s+="</svg>";box.innerHTML=s;const cr=box.querySelector(".cr");
 box.querySelectorAll(".hv").forEach(r=>{const i=+r.dataset.i;bindTip(box,r,`<b>${MS[i]}</b><br>`+ser.map(q=>`<i class="sw" style="background:${q.c}"></i>${q.n}: ${o.tf(q.v[i])}`).join("<br>"));
  r.addEventListener("mouseenter",()=>{cr.setAttribute("x1",x(i));cr.setAttribute("x2",x(i));cr.setAttribute("visibility","visible")});r.addEventListener("mouseleave",()=>cr.setAttribute("visibility","hidden"))})}

function prodChart(o){const box=el("smC3"),W=1040,H=270,L=56,R=16,T=14,B=28,mx=Math.max(...o.ton,...o.bbc,...o.tgt),st=nice(mx*1.05),hi=Math.ceil(mx*1.05/st)*st,y=v=>T+(H-T-B)*(1-v/hi),cw=(W-L-R)/n,x=i=>L+cw*(i+.5),bw=Math.min(cw*.5,56);
 let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Produksi, BBC dan Target per bulan">`+axisY(W,L,R,T,H,B,0,hi,st,v=>nf(v));
 o.ton.forEach((v,i)=>{const h=y(0)-y(v),r=Math.min(4,bw/2);s+=`<path d="M${x(i)-bw/2} ${y(0)}V${y(v)+r}a${r} ${r} 0 0 1 ${r} -${r}h${bw-2*r}a${r} ${r} 0 0 1 ${r} ${r}V${y(0)}z" fill="var(--s1)"/><text x="${x(i)}" y="${y(0)+16}" text-anchor="middle">${MS[i]}</text>`});
 for(const [a,c,dash] of [[o.bbc,"var(--s2)",0],[o.tgt,"var(--ink2)",1]]){s+=`<path d="${a.map((v,i)=>(i?"L":"M")+x(i)+" "+y(v)).join("")}" fill="none" stroke="${c}" stroke-width="2" ${dash?'stroke-dasharray="5 3"':""}/>`;a.forEach((v,i)=>s+=`<circle cx="${x(i)}" cy="${y(v)}" r="4" fill="${c}" stroke="var(--surf)" stroke-width="2"/>`)}
 o.ton.forEach((v,i)=>s+=`<text x="${x(i)}" y="${y(v)+15}" text-anchor="middle" style="fill:#fff;font-weight:600">${v/hi>.14?nf(v/1000,1)+"k":""}</text>`);
 o.ton.forEach((v,i)=>s+=`<rect class="hv" data-i="${i}" x="${x(i)-cw/2}" y="${T}" width="${cw}" height="${H-T-B}" fill="transparent"/>`);
 s+="</svg>";box.innerHTML=s;
 box.querySelectorAll(".hv").forEach(r=>{const i=+r.dataset.i;bindTip(box,r,`<b>${MS[i]}</b><br>Produksi ${nf(o.ton[i])} ton<br>BBC ${nf(o.bbc[i])} · Ach ${nf(o.ton[i]/o.bbc[i]*100,1)}%<br>Target ${nf(o.tgt[i])} · Ach ${nf(o.ton[i]/o.tgt[i]*100,1)}%`)})}

function costBars(){const box=el("smC4"),W=520,H=250,L=50,R=10,T=18,B=26,mx=Math.max(...ET.flatMap(e=>[e.y.kgA,e.y.kgB])),st=nice(mx*1.1),hi=Math.ceil(mx*1.1/st)*st,y=v=>T+(H-T-B)*(1-v/hi),cw=(W-L-R)/ET.length,bw=Math.min(cw*.32,46);
 let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="EC Rp per Kg YTD aktual vs budget per estate">`+axisY(W,L,R,T,H,B,0,hi,st,v=>nf(v));
 ET.forEach((e,i)=>{const cx=L+cw*(i+.5);
  [[e.y.kgA,"var(--s1)",-bw-1],[e.y.kgB,"var(--ref)",1]].forEach(([v,c,dx])=>{const r=4;s+=`<path d="M${cx+dx} ${y(0)}V${y(v)+r}a${r} ${r} 0 0 1 ${r} -${r}h${bw-2*r}a${r} ${r} 0 0 1 ${r} ${r}V${y(0)}z" fill="${c}"/><text x="${cx+dx+bw/2}" y="${y(v)-5}" text-anchor="middle">${nf(v)}</text>`});
  s+=`<text x="${cx}" y="${H-8}" text-anchor="middle" style="font-weight:600">${e.l}</text><rect class="hv" data-i="${i}" x="${cx-cw/2}" y="${T}" width="${cw}" height="${H-T-B}" fill="transparent"/>`});
 s+="</svg>";box.innerHTML=s;box.querySelectorAll(".hv").forEach(r=>{const e=ET[+r.dataset.i];bindTip(box,r,`<b>${e.l}</b><br>Aktual ${nf(e.y.kgA)} Rp/Kg<br>Budget ${nf(e.y.kgB)} Rp/Kg<br>Ach ${nf(e.y.kgA/e.y.kgB*100,1)}%`)})}

function stacked(){const box=el("smC6"),W=1040,H=300,L=56,R=10,T=14,B=44,cols=[];
 for(const e of ET){cols.push({l:"A",e,v:e.y.ck});cols.push({l:"B",e,v:e.y.bk})}
 const mx=Math.max(...cols.map(c=>sum(c.v))),st=nice(mx*1.05),hi=Math.ceil(mx*1.05/st)*st,y=v=>T+(H-T-B)*(1-v/hi),cw=(W-L-R)/cols.length,bw=Math.min(cw*.62,70);
 let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Komposisi EC Rp per Kg aktual dan budget">`+axisY(W,L,R,T,H,B,0,hi,st,v=>nf(v));
 cols.forEach((c,i)=>{const cx=L+cw*(i+.5);let acc=0;
  c.v.forEach((v,k)=>{const y1=y(acc),y2=y(acc+v);acc+=v;if(v>0)s+=`<rect class="sg" data-i="${i}" data-k="${k}" x="${cx-bw/2}" y="${y2}" width="${bw}" height="${Math.max(y1-y2-2,0)}" fill="${CC[k]}" rx="${k===6?3:0}"/>`});
  s+=`<text x="${cx}" y="${y(acc)-5}" text-anchor="middle" style="font-weight:600">${nf(acc)}</text><text x="${cx}" y="${H-24}" text-anchor="middle">${c.l==="A"?"A":"B"}</text>`;
  if(c.l==="A")s+=`<text x="${cx+cw/2}" y="${H-8}" text-anchor="middle" style="font-weight:600">${c.e.l}</text>`});
 s+="</svg>";box.innerHTML=s;
 box.querySelectorAll(".sg").forEach(r=>{const c=cols[+r.dataset.i],k=+r.dataset.k;bindTip(box,r,`<b>${c.e.l} · ${c.l==="A"?"Aktual":"Budget"}</b><br><i class="sw" style="background:${CC[k]}"></i>${CAT[k]}: ${nf(c.v[k])} Rp/Kg (${nf(c.v[k]/sum(c.v)*100,1)}%)<br>Total ${nf(sum(c.v))} Rp/Kg`)});
 el("smL6").innerHTML=CAT.map((c,k)=>`<span><i class="sw" style="background:${CC[k]}"></i>${c}</span>`).join("")}

function monthly(){const o=agg(sc),lb=SC.find(x=>x[0]===sc)[1];
 el("smH2").textContent="Ach. per bulan · "+lb;el("smH3").textContent="Produksi, BBC dan Target per bulan (ton) · "+lb;el("smH5").textContent="EC Rp/Kg per bulan · "+lb;el("smH7").textContent="Peta panas Rp/Kg per komponen per bulan · "+lb;
 const a1=o.ton.map((v,i)=>v/o.bbc[i]),a2=o.ton.map((v,i)=>v/o.tgt[i]),all=[...a1,...a2,1],lo=Math.floor(Math.min(...all)*20)/20-.05,hi=Math.ceil(Math.max(...all)*20)/20+.05;
 lines("smC2",[{c:"var(--s1)",v:a1,n:"Ach. BBC"},{c:"var(--s2)",v:a2,n:"Ach. Target"}],{ref:1,lo:Math.max(0,lo),hi,st:.1,fmt:v=>Math.round(v*100)+"%",tf:v=>nf(v*100,1)+"%",lab:"Ach. per bulan terhadap BBC dan Target"});
 prodChart(o);
 const ka=o.ton.map((v,i)=>sum(o.act.map(x=>x[i]))/v),kb=o.tgt.map((v,i)=>sum(o.bud.map(x=>x[i]))/v),m2=Math.max(...ka,...kb),mn=Math.min(...ka,...kb),stp=nice((m2-mn)*1.3||100,4),l2=Math.floor(mn*.95/stp)*stp,h2=Math.ceil(m2*1.03/stp)*stp;
 lines("smC5",[{c:"var(--s1)",v:ka,n:"Aktual"},{c:"var(--ink2)",d:1,v:kb,n:"Budget"}],{lo:l2,hi:h2,st:stp,fmt:v=>nf(v),tf:v=>nf(v)+" Rp/Kg",lab:"EC Rp per Kg per bulan, aktual vs budget"});
 tables()}
const seg=el("smSc");SC.forEach(([k,l])=>{const b=document.createElement("button");b.textContent=l;b.setAttribute("aria-pressed",k===sc);b.onclick=()=>{sc=k;seg.querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",x===b));monthly()};seg.appendChild(b)});
kpis();hbars();costBars();stacked();monthly();
})();
