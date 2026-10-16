import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source = fs.readFileSync('worker/src/metrics.js', 'utf8');
const {metrics} = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
let writes = [], limited = false;
const DB = {prepare(sql) { return {bind(...args) {return {async first() {return limited ? null : {count:1}}, async run(){writes.push(args)}}}}}};
const req = (body, headers={}, method='POST') => new Request('https://threeohfivestudios.com/api/events', {method,headers:{Origin:'https://threeohfivestudios.com','Content-Type':'application/json',...headers},...(method==='POST'?{body:JSON.stringify(body)}:{})});
const good = {event:'live_click',scene:'website',project:'aero'};
assert.equal((await metrics(req(good), {DB})).status,204);
assert.deepEqual(writes[0].slice(1),['website','live_click','aero']);
for (const bad of [{...good,project:'unknown'}, {...good,scene:'unknown'}, {event:'page_view',scene:'temple',project:'aero'}, null]) assert.equal((await metrics(req(bad),{DB})).status,400);
assert.equal((await metrics(req(good,{Origin:'https://evil.example'}),{DB})).status,403);
assert.equal((await metrics(req(good,{},'GET'),{DB})).status,405);
assert.equal((await metrics(req('x'.repeat(513)),{DB})).status,413);
assert.equal((await metrics(req(good,{DNT:'1'}),{DB})).status,204);
assert.equal(writes.length,1);
limited = true;
assert.equal((await metrics(req(good),{DB})).status,429);
assert.equal(writes.length,1);
const client = fs.readFileSync('assets/metrics.js','utf8');
function browser(path='/portfolio/', opt={}) {
 const events={}, sent=[], storage=new Map();
 const location=new URL('https://threeohfivestudios.com'+path);
 const document={visibilityState:'visible',addEventListener:(name,fn)=>events[name]=fn};
 const navigator={sendBeacon:(url,body)=>{sent.push(body);return true},...opt};
 const context={location,document,navigator,window:{},sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},Blob,URL,Set};
 vm.runInNewContext(client,context);
 return {events,sent,context,async payloads(){return Promise.all(sent.map(async b=>JSON.parse(await b.text())))},click(href,dataset={}){events.click({isTrusted:true,type:'click',target:{closest:()=>({href:new URL(href,location).href,dataset})}})}};
}
let b=browser();b.events.visibilitychange();assert.equal(b.sent.length,1);
b.context.window.portfolioMetric('project_view','aero');b.context.window.portfolioMetric('project_view','aero');assert.equal(b.sent.length,2);
b.context.document.visibilityState='hidden';b.context.window.portfolioMetric('contact_click');assert.equal(b.sent.length,2);
for(const opt of [{doNotTrack:'1'},{globalPrivacyControl:true},{webdriver:true}])assert.equal(browser('/portfolio/',opt).sent.length,0);
assert.equal(browser('/portfolio/pond-study.html').sent.length,0);
b=browser('/');b.click('/recent-work-autodex/');b.click('https://autodx.io/');b.click('/portfolio/');
assert.deepEqual((await b.payloads()).map(x=>x.event),['page_view','project_click','live_click','portfolio_click']);
assert.equal((await b.payloads())[1].project,'autodex');
console.log('Metrics client and endpoint checks passed');
const reportSource = fs.readFileSync('worker/src/report.js','utf8');
const {report} = await import('data:text/javascript;base64,'+Buffer.from(reportSource).toString('base64'));
let reads = 0;
const reportEnv = {METRICS_REPORT_KEY:'test-only',DB:{prepare(){return {bind(){return {async all(){reads++;return {results:[],meta:{rows_read:0}}}}}}}}};
assert.equal((await report(new Request('https://example.com/api/metrics-report'),reportEnv)).status,403);
assert.equal(reads,0);
const authorized = () => new Request('https://example.com/api/metrics-report',{headers:{Authorization:'Bearer test-only'}});
assert.equal((await report(authorized(),reportEnv)).status,200);
assert.equal((await report(authorized(),reportEnv)).status,200);
assert.equal(reads,1);
assert.equal((await report(authorized(),{})).status,403);

limited = false;
assert.equal((await metrics(req({event:'game_launch',scene:'games',project:'pyxel'}),{DB})).status,204);
assert.equal((await metrics(req({event:'game_launch',scene:'games',project:'shop'}),{DB})).status,400);
b=browser('/portfolio/pyxel/');
b.click('https://lrakoto.github.io/Pyxel2/',{metricProject:'pyxel',metricEvent:'game_launch'});
assert.deepEqual((await b.payloads()).map(x=>x.event),['page_view','game_launch']);
assert.equal((await b.payloads())[1].scene,'games');
const rangeRequest = days => new Request('https://example.com/api/metrics-report?days='+days,{headers:{Authorization:'Bearer test-only'}});
assert.equal((await report(rangeRequest(7),reportEnv)).status,200);
assert.equal((await report(rangeRequest(90),reportEnv)).status,200);
assert.equal(reads,3);
const ninety = await (await report(rangeRequest(90),reportEnv)).json();
assert.equal(ninety.days,90); assert.equal(reads,3);
assert.equal((await report(rangeRequest(999),reportEnv)).status,400);
assert.equal(reads,3);

// asset activity never carries a catalog item, project, or search value.
const artdexEvents = ['page_view','asset_view','asset_download','filter_use','asset_save'];
for (const event of artdexEvents) {
  const before = writes.length;
  assert.equal((await metrics(req({event,scene:'artdex',project:''}),{DB})).status,204);
  assert.deepEqual(writes[before].slice(1),['artdex',event,'']);
}
for (const input of [
  ...artdexEvents.map(event=>({event,scene:'artdex',project:'aero'})),
  ...artdexEvents.slice(1).flatMap(event=>['website','temple','redwoods','forest','games'].map(scene=>({event,scene}))),
  {event:'project_view',scene:'artdex',project:'aero'},
  {event:'resume_click',scene:'artdex'},
  {event:'asset_view',scene:'artdex',email:'private@example.test'},
  {event:'filter_use',scene:'artdex',query:'private search'},
]) {
  const before=writes.length;
  assert.equal((await metrics(req(input),{DB})).status,400);
  assert.equal(writes.length,before);
}
const beforeOptOut=writes.length;
assert.equal((await metrics(req({event:'asset_view',scene:'artdex'},{'Sec-GPC':'1'}),{DB})).status,204);
assert.equal(writes.length,beforeOptOut);

// exercise the hosted dashboard script with both scenes so visits stay separate.
const plugin = fs.readFileSync('root/mu-plugins/305-metrics.php','utf8');
const dashboardScript = plugin.match(/<script>\s*([\s\S]*?)\s*<\/script>/)[1]
  .replace(/<\?php echo wp_json_encode\(wp_create_nonce\('studios_metrics_report'\)\); \?>/, '"test-nonce"');
function node(tag,text='') {return {tag,textContent:text,children:[],append(...children){this.children.push(...children)},replaceChildren(){this.children=[]},addEventListener(){}};}
const content=node('div'), status=node('p'), range=node('select');range.value='30';
const fixtureRows = [
  {day:'2026-10-15',scene:'website',event:'page_view',project:'',count:3},
  {day:'2026-10-15',scene:'artdex',event:'page_view',project:'',count:11},
  {day:'2026-10-15',scene:'artdex',event:'asset_download',project:'',count:7}
];
vm.runInNewContext(dashboardScript,{
  document:{hidden:false,createElement:tag=>node(tag),getElementById:id=>({'metrics-content':content,'metrics-status':status,'metrics-range':range})[id],addEventListener(){}},
  fetch:async()=>({ok:true,status:200,json:async()=>({success:true,data:{rows:fixtureRows,days:30,updated:'2026-10-15T00:00:00Z'}})}),
  ajaxurl:'/wp-admin/admin-ajax.php',URLSearchParams,Date,setInterval(){}
});
await new Promise(resolve=>setImmediate(resolve));
const sections=content.children;
assert.equal(sections[0].textContent,'Artdex');
assert.equal(sections[1].children[0].children[0].textContent,11);
assert.equal(sections[1].children[2].children[0].textContent,7);
const portfolioHeading=sections.findIndex(el=>el.textContent==='Portfolio & website');
assert.ok(portfolioHeading>1);
assert.equal(sections[portfolioHeading+1].children[0].children[0].textContent,3);
assert.ok(status.textContent.startsWith('Last 30 days'));
console.log('Artdex collector and hosted dashboard checks passed');
