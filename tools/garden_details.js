/* materials stay reversible: the comparison must keep the old gate exactly
   as it was, including shared lacquer and metal materials. */
function refineGardenGate() {
  if(GARDEN_STYLE!=='temple' || !WORLD.torii)return;
  const cache=new Map();
  WORLD.torii.traverse(o=>{
    if(!o.isMesh || !o.material.isMeshStandardMaterial)return;
    const base=o.material;
    if(!cache.has(base)){
      const mat=base.clone(),metal=mat.metalness>.3;
      mat.roughness=metal?.64:.76;
      if(mat.normalScale)mat.normalScale.multiplyScalar(.72);
      mat.onBeforeCompile=sh=>{
        sh.vertexShader='varying vec3 vGateP;\n'+sh.vertexShader;
        sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvGateP=position;');
        sh.fragmentShader='varying vec3 vGateP;\n'+sh.fragmentShader;
        sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
          ${metal ? `
          float patina=.5+.5*sin(vGateP.x*17.+sin(vGateP.y*23.)+vGateP.z*19.);
          patina=smoothstep(.62,.96,patina);
          diffuseColor.rgb=mix(diffuseColor.rgb,diffuseColor.rgb*vec3(.49,.66,.54),patina*.32);` : `
          float axis=abs(vGateP.x)>1.?vGateP.y:vGateP.x;
          float grain=.5+.5*sin(axis*185.+sin(vGateP.y*2.7+vGateP.x*.9)*2.);
          float filterGrain=1.-smoothstep(.18,.9,fwidth(axis*185.));
          diffuseColor.rgb*=1.-grain*filterGrain*.10;
          diffuseColor.rgb*=vec3(1.035,.97,.94);`}`);
      };
      mat.customProgramCacheKey=()=> 'garden-gate-grain-patina-'+metal;
      cache.set(base,mat);
    }
    gardenEdit(o,'material',cache.get(base));
  });
}
function refineRedwoodBark(mat) {
  const compile=mat.onBeforeCompile;
  mat.onBeforeCompile=sh=>{
    compile(sh);
    sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
      float barkAge=gn(vGardenP*vec3(.65,.12,.65));
      float dampFoot=1.-smoothstep(.3,3.8,vGardenP.y);
      diffuseColor.rgb*=mix(.76,1.08,barkAge)*(1.-dampFoot*.15);
      diffuseColor.rgb=mix(diffuseColor.rgb,diffuseColor.rgb*vec3(.77,.89,.66),dampFoot*barkAge*.22);`);
  };
  mat.customProgramCacheKey=()=> 'redwood-weathered-bark-2';
}
function addPondFlowersAndShore() {
  const pads=GARDEN.group.getObjectByName('pond lily pads');
  if(!pads || !pads.count)return;
  const parts=[],matrix=new THREE.Matrix4(),q=new THREE.Quaternion(),up=new THREE.Vector3(0,1,0);
  for(let ring=0;ring<2;ring++)for(let i=0;i<7;i++){
    const shape=new THREE.Shape();shape.moveTo(0,0);shape.quadraticCurveTo(-.07,.12,0,.26);shape.quadraticCurveTo(.07,.12,0,0);
    const geo=new THREE.ShapeGeometry(shape,4),p=geo.attributes.position;
    for(let n=0;n<p.count;n++){const t=p.getY(n)/.26;p.setXYZ(n,p.getX(n),.02+t*t*(ring?.13:.075),p.getY(n)*(ring?.72:1));}
    geo.rotateY(i/7*TAU+ring*.4);geo.computeVertexNormals();parts.push(geo);
  }
  const count=Math.min(LOW?3:7,pads.count);
  const petalMat=new THREE.MeshStandardMaterial({color:0xc5a7a2,roughness:.67,side:THREE.DoubleSide,envMapIntensity:.6});
  petalMat.onBeforeCompile=pads.material.onBeforeCompile;petalMat.customProgramCacheKey=()=> 'pond-petal-rocking-1';
  const flowers=new THREE.InstancedMesh(mergeGeos(parts),petalMat,count);
  const hearts=new THREE.InstancedMesh(new THREE.SphereGeometry(.04,8,5),new THREE.MeshStandardMaterial({color:0x977840,roughness:.83}),count);
  for(let i=0;i<count;i++){
    pads.getMatrixAt(Math.floor(i*pads.count/count),matrix);
    const p=new THREE.Vector3().setFromMatrixPosition(matrix);p.y=.095;
    q.setFromAxisAngle(up,i*2.399);matrix.compose(p,q,new THREE.Vector3(1,1,1));flowers.setMatrixAt(i,matrix);
    p.y+=.045;matrix.compose(p,q,new THREE.Vector3(1,1,1));hearts.setMatrixAt(i,matrix);
  }
  for(const m of [flowers,hearts]){m.layers.set(1);m.renderOrder=6;m.frustumCulled=false;GARDEN.group.add(m);}
  flowers.name='quiet water lilies';hearts.name='water lily centres';
  const rnd=mulberry32(610305),stone=gardenSurface(new THREE.MeshStandardMaterial({color:0x41483b,roughness:.72,envMapIntensity:.6}),'stone');
  const pebbles=new THREE.InstancedMesh(erodedRockGeo(1,4911,1),stone,LOW?75:190);let placed=0;
  for(let i=0;i<5000 && placed<pebbles.count;i++){
    const side=i%2?1:-1,x=side*(6.5+rnd()*8),z=-17+rnd()*28,y=gardenGround(x,z);
    if(y<-.12 || y>.14)continue;
    const size=.05+rnd()*.10;q.setFromAxisAngle(up,rnd()*TAU);
    matrix.compose(new THREE.Vector3(x,y+size*.1,z),q,new THREE.Vector3(size*1.3,size*.55,size));pebbles.setMatrixAt(placed++,matrix);
  }
  pebbles.count=placed;pebbles.receiveShadow=true;pebbles.frustumCulled=false;pebbles.name='shoreline pebble transition';GARDEN.group.add(pebbles);
}
