"""The study must stay a valid asset swap, with the approved camera intact."""
import json
import re
import shutil
import struct
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PAGE=ROOT/'temple-study.html'

class TempleStudyTests(unittest.TestCase):
    @unittest.skipIf(shutil.which('node') is None, 'node unavailable')
    def test_study_and_vendored_loader_parse(self):
        source=PAGE.read_text()
        script=re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>',source,re.S)[-1]
        result=subprocess.run(['node','--check'],input=script,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        result=subprocess.run(['node','--check',str(ROOT/'assets/temple-study/GLTFLoader.r149.js')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_comparison_preserves_camera_and_window_settings(self):
        original=(ROOT/'tools/templates/temple-original.html').read_text();study=PAGE.read_text()
        for pattern in [r'const CAM = \[.*?\n\];',r'const TUNE = \{.*?\n\};',r'function buildTemple\(\) \{.*?\n\}',r'function applyCamera\(\) \{.*?\n\}']:
            self.assertEqual(re.search(pattern,original,re.S).group(),re.search(pattern,study,re.S).group())
        self.assertIn("fetch('/__tune/study/save'",study)
        self.assertIn('depthBuffer: true, stencilBuffer: true, samples:',study)
        self.assertIn('type: LOW ? THREE.UnsignedByteType : THREE.HalfFloatType, depthBuffer: true, stencilBuffer: true',study)
        self.assertNotIn("fetch('/__tune/temple/save'",study)

    def test_export_has_finite_geometry_and_complete_pbr_maps(self):
        data=(ROOT/'assets/temple-study/temple-quality.glb').read_bytes()
        magic,version,length=struct.unpack_from('<4sII',data)
        self.assertEqual((magic,version,length),(b'glTF',2,len(data)))
        size,kind=struct.unpack_from('<II',data,12);self.assertEqual(kind,0x4e4f534a)
        doc=json.loads(data[20:20+size]);binary=data[28+size:]
        self.assertEqual(len(doc['meshes']),1)
        self.assertLessEqual(len(doc['meshes'][0]['primitives']),6)
        total=0
        for prim in doc['meshes'][0]['primitives']:
            for name in ('POSITION','NORMAL','TEXCOORD_0'):
                accessor=doc['accessors'][prim['attributes'][name]]
                view=doc['bufferViews'][accessor['bufferView']]
                count=accessor['count']*(2 if name=='TEXCOORD_0' else 3)
                self.assertEqual(accessor['componentType'],5126)
                offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
                values=struct.unpack_from('<'+'f'*count,binary,offset)
                self.assertTrue(all(-1e5<v<1e5 for v in values))
                if name=='TEXCOORD_0':self.assertTrue(all(-.001<=v<=1.001 for v in values))
            pos=doc['accessors'][prim['attributes']['POSITION']]
            self.assertGreaterEqual(pos['min'][1],6.9)
            self.assertLessEqual(pos['max'][1],25.4)
            self.assertGreaterEqual(pos['min'][2],-51.4)
            self.assertLessEqual(pos['max'][2],-36.6)
            self.assertGreaterEqual(pos['min'][0],-15.8)
            self.assertLessEqual(pos['max'][0],15.8)
            mat=doc['materials'][prim['material']]
            self.assertIn('baseColorTexture',mat['pbrMetallicRoughness'])
            self.assertIn('normalTexture',mat)
            self.assertIn('occlusionTexture',mat)
            total+=doc['accessors'][prim['indices']]['count']//3
        self.assertGreater(total,40000);self.assertLess(total,160000)
        self.assertLess(len(data),16*1024*1024)
        self.assertTrue((ROOT/'assets/temple-study/temple-bounce.png').stat().st_size>1000)

    @unittest.skipIf(shutil.which('node') is None, 'node unavailable')
    def test_swap_and_failed_load_leave_original_windows_and_weather(self):
        source=PAGE.read_text();start=source.index('const TEMPLE_STUDY =');end=source.index('\nfunction buildMaple',start)
        code=source[start:end]
        live=(ROOT/'index.html').read_text()
        live_code=live[live.index('const TEMPLE_STUDY ='):live.index('\nfunction buildMaple',live.index('const TEMPLE_STUDY ='))]
        self.assertNotIn('<aside class="study-controls"',live)
        self.assertNotIn('name="robots" content="noindex',live)
        self.assertIn("fetch('/__tune/temple/save'",live)
        self.assertNotIn('assets/temple-study/',live)
        for asset in ('temple-quality.glb','temple-bounce.png','GLTFLoader.r149.js','THREE-LICENSE.txt'):
            self.assertTrue((ROOT/'assets/temple'/asset).is_file(),asset)
        cases=[[code,True],[live_code,False]]
        harness=r"""
const assert=require('node:assert/strict'),vm=require('node:vm');
const THREE=require('./assets/three.min.js');
(async()=>{for(const [CODE,controls] of CASES)for(const fail of [false,true]){
 const scene=new THREE.Scene(),temple=new THREE.Group(),WORLD={temple,key:{shadow:{needsUpdate:false}}};
 const original=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());
 const paper=new THREE.Mesh(new THREE.PlaneGeometry(),new THREE.MeshBasicMaterial());temple.add(original,paper);scene.add(temple);
 const mist=new THREE.Mesh(new THREE.PlaneGeometry(),new THREE.MeshBasicMaterial());scene.add(mist);
 const model=new THREE.Group();const enhanced=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshStandardMaterial());model.add(enhanced);
 const elements={};const document={getElementById:id=>controls?(elements[id]||(elements[id]={addEventListener(){},setAttribute(k,v){this[k]=v}})):null};
 class Loader{loadAsync(){return fail?Promise.reject(Error('offline')):Promise.resolve({scene:model})}}
 class Textures{loadAsync(){return Promise.resolve(new THREE.Texture())}}
 const ctx={THREE:{...THREE,GLTFLoader:Loader,TextureLoader:Textures},scene,WORLD,document,maxAniso:4,buildTemple(){},applyTempleDepth(){},console:{warn(){}}};
 vm.createContext(ctx);vm.runInContext(CODE,ctx);await ctx.buildTempleStudy();
 assert.equal(paper.visible,true);assert.equal(mist.visible,true);
 if(fail){assert.equal(original.visible,true);assert.equal(scene.children.length,2);if(controls)assert.match(elements['study-status'].textContent,/unavailable/);continue;}
 assert.equal(original.visible,false);assert.equal(model.visible,true);assert(enhanced.geometry.attributes.uv2);if(controls)assert.equal(elements['study-model'].disabled,false);
 ctx.setTempleStudy(false);assert.equal(original.visible,true);assert.equal(model.visible,false);
 ctx.setTempleStudy(true);assert.equal(original.visible,false);assert.equal(model.visible,true);assert.equal(WORLD.key.shadow.needsUpdate,true);
}})().catch(e=>{console.error(e);process.exitCode=1});
"""
        result=subprocess.run(['node','-e','const CASES='+json.dumps(cases)+';\n'+harness],cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
