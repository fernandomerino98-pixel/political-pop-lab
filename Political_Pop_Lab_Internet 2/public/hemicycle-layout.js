// Geometry is based on continuous angular sectors, not row filling order.
function layoutHemicycle(seats){
 const keys=['left','center','right'],classify=p=>p===null?'unknown':p<-.7?'left':p>.7?'right':'center';
 const groups=Object.fromEntries([...keys,'unknown'].map(k=>[k,seats.filter(s=>classify(s.position)===k).sort((a,b)=>(a.position??0)-(b.position??0)||a.number-b.number)]));
 const rows=Math.max(seats.filter(s=>s.position!==null).length>=18?3:1,Math.ceil(Math.sqrt(Math.max(...keys.map(k=>groups[k].length),1)/5))),points=[];
 keys.forEach((key,sector)=>{
  const group=groups[key],radii=Array.from({length:rows},(_,i)=>rows===1?250:145+i*175/(rows-1)),total=radii.reduce((a,b)=>a+b,0);
  const exact=radii.map(r=>group.length*r/total),counts=exact.map(Math.floor);let left=group.length-counts.reduce((a,b)=>a+b,0);
  const order=exact.map((v,i)=>({i,f:v-counts[i]})).sort((a,b)=>b.f-a.f);
  for(let i=0;i<left;i++)counts[order[i].i]++;
  let index=0;const start=Math.PI-sector*Math.PI/3-.045,end=Math.PI-(sector+1)*Math.PI/3+.045;
  radii.forEach((radius,row)=>{const count=counts[row],spacing=(start-end)/Math.max(1,count),dot=Math.max(3,Math.min(29,rows===1?29:175/(rows-1)*.39,radius*spacing*.4));
   for(let j=0;j<count;j++){const angle=start-(j+.5)*spacing;points.push({seat:group[index++],bloc:key,row,angle,x:360+Math.cos(angle)*radius,y:365-Math.sin(angle)*radius,r:dot})}
  });
 });
 const unknown=groups.unknown,columns=Math.min(12,Math.max(1,unknown.length));
 unknown.forEach((seat,i)=>points.push({seat,bloc:'unknown',row:Math.floor(i/columns),x:360-(columns-1)*25+(i%columns)*50,y:460+Math.floor(i/columns)*52,r:19}));
 return {points,groups,height:unknown.length?500+Math.ceil(unknown.length/columns)*52:410};
}
if(typeof module!=='undefined')module.exports={layoutHemicycle};
