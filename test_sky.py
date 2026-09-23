"""The visible sky and reflected sky share a spherical procedural painting."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


@unittest.skipIf(shutil.which("node") is None, "node is not installed")
class SkyTests(unittest.TestCase):
    def test_sphere_is_continuous_and_moon_can_turn_off(self):
        page = Path(__file__).with_name("index.html").read_text()
        helpers = page[page.index("const clamp  ="):page.index("/* ------------------------------------------------------- 0b")]
        sky = page[page.index("const SKY = {"):page.index("async function texSky(")]
        harness = r"""
const assert = require('node:assert/strict');
const TUNE = {moonSize:.76, moonBright:.285};
const paint = skyPainter(0);
function at(y, az) {
  const r = Math.sqrt(1-y*y);
  return [...paint(Math.sin(az)*r, y, -Math.cos(az)*r)];
}
for (const y of [-.9,-.08,-.025,0,.3,.9]) {
  const a=at(y,Math.PI-1e-8), b=at(y,-Math.PI+1e-8);
  a.forEach((v,i)=>assert.ok(Number.isFinite(v) && Math.abs(v-b[i])<.001));
}
for (const y of [-.08,-.025,0]) for (const az of [0,.2,1.5,-2.5]) {
  const a=at(y-1e-8,az), b=at(y+1e-8,az);
  a.slice(0,3).forEach((v,i)=>assert.ok(Math.abs(v-b[i])<.001, 'horizon ring'));
}
TUNE.moonBright=0;
const off=skyPainter(0);
const el=SKY.moonElevation, az=SKY.moonAzimuth;
const dir=[Math.sin(az)*Math.cos(el),Math.sin(el),-Math.cos(az)*Math.cos(el)];
const a=[...off(...dir)];
SKY.moonAzimuth+=1;
const b=[...skyPainter(0)(...dir)];
assert.deepEqual(a,b,'a disabled moon must not leave a dark disc');
"""
        result = subprocess.run(["node", "-e", helpers + sky + harness], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_baked_cloud_light_favors_the_moon_facing_edge(self):
        page = Path(__file__).with_name("index.html").read_text()
        helpers = page[page.index("const clamp  ="):page.index("/* ------------------------------------------------------- 0b")]
        sky = page[page.index("const SKY = {"):page.index("async function buildEnvironment()")]
        harness = r"""
const assert=require('node:assert/strict');
const LOW=true, TUNE={moonSize:.76,moonBright:.285};
function cvs(width,height){
 const context={createImageData:(w,h)=>({data:new Uint8ClampedArray(w*h*4)}),
   putImageData(image){this.image=image;},beginPath(){},arc(){},fill(){}};
 return {width,height,getContext:()=>context};
}
(async()=>{
 const canvas=await texSky(0,SKY.generation), pixels=canvas.getContext('2d').image.data;
 const paint=skyPainter(0), W=canvas.width,H=canvas.height;
 const moon=canvas.moonLight.direction;
 let lit=0,dark=0,litLoss=0,darkLoss=0;
 for(let y=H*.30|0;y<H*.47;y+=3) for(let x=0;x<W;x+=3){
  const az=(x/W-.5)*TAU,el=Math.PI*(.5-y/H);
  const d=[Math.cos(az)*Math.cos(el),Math.sin(el),Math.sin(az)*Math.cos(el)];
  const raw=[...paint(...d)]; if(raw[6]<10)continue;
  const dp=d.reduce((v,a,i)=>v+a*moon[i],0);
  const t=moon.map((a,i)=>a-d[i]*dp),l=Math.hypot(...t); if(l<.01)continue;
  const sample=sign=>{const q=d.map((a,i)=>a+sign*t[i]/l*.006),n=Math.hypot(...q);return paint(...q.map(a=>a/n))[3];};
  const slope=sample(-1)-sample(1); if(Math.abs(slope)<.055)continue;
  const across=[d[1]*t[2]-d[2]*t[1],d[2]*t[0]-d[0]*t[2],d[0]*t[1]-d[1]*t[0]];
  const side=sign=>{const q=d.map((a,i)=>a+sign*across[i]/l*.006),n=Math.hypot(...q);return paint(...q.map(a=>a/n))[3];};
  const cosine=slope/Math.hypot(slope,side(-1)-side(1));
  if(slope>0 && cosine<.85)continue;
  const loss=(raw[2]-pixels[(y*W+x)*4+2])/raw[6];
  if(slope>0){lit++;litLoss+=loss;} else {dark++;darkLoss+=loss;}
 }
 assert.ok(lit>20 && dark>20,'exercise cloud edges on both sides of the moon');
 assert.ok(litLoss/lit<.25,'keep the moon-facing broad light');
 assert.ok(darkLoss/dark>.90,'remove broad light from the far edges');
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
        result = subprocess.run(["node", "-e", helpers + sky + harness], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stale_sky_bake_cannot_replace_newer_sky(self):
        page = Path(__file__).with_name("index.html").read_text()
        build = re.search(r"async function buildEnvironment\(\) \{.*?^\}", page, re.S | re.M).group(0)
        harness = r"""
const assert=require('node:assert/strict');
const pending=[], disposed=[];
const SKY={generation:0, texture:null, environment:null, aspect:-1};
const scene={}, renderer={};
const buildSkyShimmer=()=>{};
const aspectFix=()=>.4;
const refreshSky=()=>{throw Error('unnecessary rebake');};
const texSky=()=>new Promise(resolve=>pending.push(resolve));
const tx=id=>({id,dispose(){disposed.push('texture:'+id);}});
const THREE={RepeatWrapping:1,EquirectangularReflectionMapping:2,
 PMREMGenerator:class {compileEquirectangularShader(){} dispose(){}
 fromEquirectangular(t){return {texture:{id:t.id},dispose(){disposed.push('environment:'+t.id);}};}}};
(async()=>{
 const first=buildEnvironment(), latest=buildEnvironment();
 pending[1]('latest'); await latest;
 pending[0]('stale'); await first;
 assert.equal(scene.background.id,'latest');
 assert.equal(scene.environment.id,'latest');
 assert.equal(SKY.aspect,.4);
 const next=buildEnvironment(); pending[2]('next'); await next;
 assert.deepEqual(disposed,['texture:latest','environment:latest']);
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
        result = subprocess.run(["node", "-e", build + harness], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

