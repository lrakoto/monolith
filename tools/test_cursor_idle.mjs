import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
for (const file of ['index.html','redwoods.html','forest.html']) {
  const source=fs.readFileSync(file,'utf8');
  const start=source.indexOf('function wireCursor() {');
  const end=source.indexOf('\n/* The tile',start);
  const handlers={}, pending=new Map();let next=0;
  const dot={style:{},classList:{add(){},remove(){}}};
  const context={COARSE:false,REDUCE:false,$:()=>dot,$$:()=>[],vpW:()=>390,vpH:()=>844,RIG:{},document:{hidden:false,addEventListener:(name,fn)=>handlers[name]=fn},addEventListener:(name,fn)=>handlers[name]=fn,lerp:(a,b,k)=>a+(b-a)*k,requestAnimationFrame:fn=>{pending.set(++next,fn);return next}};
  vm.runInNewContext(source.slice(start,end)+'\nwireCursor();',context);
  const frameStart=source.indexOf('function frame(now) {\n  if (!running) return;');
  const frameEnd=source.indexOf('\nconst TIMER',frameStart);
  let scheduled=0;
  const paused={running:true,tPrev:0,document:{getElementById:()=>({open:true})},setTimeout:(fn,delay)=>{assert.equal(delay,100);scheduled++;}};
  vm.runInNewContext(source.slice(frameStart,frameEnd)+'\nframe(1000);',paused);
  assert.equal(scheduled,1,file+': reading panel defers rendering');
  assert.equal(paused.tPrev,1000);
  assert.equal(pending.size,0, file+': no idle animation');
  handlers.pointermove({clientX:10,clientY:20});assert.equal(pending.size,1);
  for(let i=0;pending.size && i<100;i++){const jobs=[...pending.values()];pending.clear();jobs.forEach(fn=>fn());}
  assert.equal(pending.size,0,file+': settles');
  handlers.pointermove({clientX:90,clientY:120});context.document.hidden=true;
  for(const fn of pending.values())fn();pending.clear();
  context.document.hidden=false;handlers.visibilitychange();assert.equal(pending.size,1,file+': resumes');
}
console.log('Cursor idle/resume behavior passed for all live scenes');
