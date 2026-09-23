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

    def test_stale_sky_bake_cannot_replace_newer_sky(self):
        page = Path(__file__).with_name("index.html").read_text()
        build = re.search(r"async function buildEnvironment\(\) \{.*?^\}", page, re.S | re.M).group(0)
        harness = r"""
const assert=require('node:assert/strict');
const pending=[], disposed=[];
const SKY={generation:0, texture:null, environment:null, aspect:-1};
const scene={}, renderer={};
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

