/* the garden is one reversible layer. the temple-only study remains available
   so a lighting change cannot masquerade as a better model. */
const GARDEN_STYLE = typeof GARDEN_KIND==='undefined' ? 'temple' : GARDEN_KIND;
const GARDEN = { original: [], trees: [], group: null, ready: false, edits: [], active: true };
function rememberStudyMaple(seed, x, z, scale) {
  const tree = buildMaple(seed, x, z, scale);
  GARDEN.original.push(tree); GARDEN.trees.push([seed, x, z, scale]);
}
function rememberStudyRocks() {
  const before = new Set(scene.children); buildRocks();
  scene.children.forEach(o => { if (!before.has(o)) GARDEN.original.push(o); });
}
function gardenEdit(object, key, value) {
  GARDEN.edits.push({ object, key, original: object[key], study: value });
}
function setGardenStudy(active) {
  GARDEN.active = active;
  GARDEN.frames=0;GARDEN.elapsed=0;
  if (!GARDEN.ready) return;
  GARDEN.group.visible = active;
  GARDEN.originalGroup.visible = !active;
  GARDEN.original.forEach(o => { o.visible = !active; });
  GARDEN.edits.forEach(e => { e.object[e.key] = active ? e.study : e.original; });
  if (WORLD.key) WORLD.key.shadow.needsUpdate = true;
}

const GARDEN_BANKS = [
  [-9.2, 5.4, 6.3, 5.5, .62], [10.8, 3.2, 6.6, 7.0, .46],
  [-14, -11, 7.8, 14, .52], [15.4, -14.5, 7.7, 16, .58],
  [-19, -33, 9, 14, .30], [20, -35, 9, 15, .26]
];
function gardenBankHeight(bank, x, z) {
  const [cx, cz, rx, rz, top] = bank;
  const u = (x-cx)/rx, v = (z-cz)/rz;
  const r = Math.hypot(u,v) + .035*Math.sin(u*8+v*3)*Math.sin(v*7);
  return -1.62 + (top+1.62)*(1-smooth(.15,1,r));
}
function gardenGround(x, z) {
  const edge=Math.hypot(x/21,(z+4)/18)+.028*Math.sin(x*.66+z*.31)+.018*Math.sin(z*1.1-x*.27);
  let y=-1.55*(1-smooth(.65,1.03,edge));
  GARDEN_BANKS.forEach(b => { y=Math.max(y,gardenBankHeight(b,x,z)); });
  return y;
}
function gardenSurface(mat, kind) {
  mat.onBeforeCompile = sh => {
    sh.vertexShader='varying vec3 vGardenP; varying vec3 vGardenN;\n'+sh.vertexShader;
    sh.vertexShader=sh.vertexShader.replace('#include <worldpos_vertex>',`#include <worldpos_vertex>
      vec4 gp=vec4(transformed,1.);
      #ifdef USE_INSTANCING
      gp=instanceMatrix*gp;
      #endif
      vGardenP=(modelMatrix*gp).xyz;
      vGardenN=normalize(mat3(modelMatrix)*objectNormal);`);
    sh.fragmentShader=`varying vec3 vGardenP; varying vec3 vGardenN;
      float gn(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
      vec4 h=vec4(dot(i,vec3(1,57,113)))+vec4(0,1,57,58);
      vec4 a=fract(sin(h)*43758.5453),b=fract(sin(h+113.)*43758.5453);
      return mix(mix(mix(a.x,a.y,f.x),mix(a.z,a.w,f.x),f.y),mix(mix(b.x,b.y,f.x),mix(b.z,b.w,f.x),f.y),f.z);}
      `+sh.fragmentShader;
    const color = kind==='bark' ? `
      float grain=gn(vGardenP*vec3(16.,1.1,16.));
      float grooves=pow(.5+.5*sin(vGardenP.x*46.+gn(vGardenP*2.)*8.+vGardenP.y*.5),8.);
      diffuseColor.rgb*=mix(.58,1.25,grain)*(1.-grooves*.22);` : `
      float mottling=gn(vGardenP*1.5)*.65+gn(vGardenP*5.7)*.35;
      float fleck=gn(vGardenP*31.);
      float moss=smoothstep(.43,.68,mottling)*smoothstep(.28,.85,vGardenN.y);
      diffuseColor.rgb*=mix(.72,1.17,mottling)*mix(.89,1.07,fleck);
      diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.025,.043,.012),moss*${kind==='soil'?'.85':'.64'});
      float wet=1.-smoothstep(.08,.54,vGardenP.y);
      diffuseColor.rgb*=1.-wet*.22;`;
    sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\n'+color);
    /* world-space relief keeps rock seams and stretched trunk UVs out of the
       close view; derivative filtering lets the fine grain recede at distance. */
    sh.fragmentShader=sh.fragmentShader.replace('#include <normal_fragment_maps>',`#include <normal_fragment_maps>
      float gardenRelief=${kind==='bark'?'grain*.025-grooves*.009':'gn(vGardenP*9.)*.032+fleck*.008'};
      gardenRelief*=1.-smoothstep(.2,1.,length(fwidth(vGardenP*9.)));
      vec3 gx=dFdx(-vViewPosition),gy=dFdy(-vViewPosition);
      vec3 gr1=cross(gy,normal),gr2=cross(normal,gx);
      float gd=dot(gx,gr1)*faceDirection;
      normal=normalize(abs(gd)*normal-sign(gd)*(dFdx(gardenRelief)*gr1+dFdy(gardenRelief)*gr2));`);
  };
  mat.customProgramCacheKey=()=> 'garden-surface-'+kind+'-1';
  return mat;
}
function gardenWind(mat, strength, leaf = false) {
  mat.onBeforeCompile=sh=>{
    sh.uniforms.uGardenTime=WET_TIME;
    if(leaf){
      sh.vertexShader='varying vec2 vGardenLeaf;\n'+sh.vertexShader;
      sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvGardenLeaf=position.xy;');
      sh.fragmentShader='varying vec2 vGardenLeaf;\n'+sh.fragmentShader;
      sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
        float rib=1.-smoothstep(.008,.018+fwidth(vGardenLeaf.x),abs(vGardenLeaf.x));
        float edgeShade=smoothstep(.05,.38,abs(vGardenLeaf.x));
        float tipShade=smoothstep(.62,1.,vGardenLeaf.y);
        diffuseColor.rgb*=1.-edgeShade*.16-tipShade*.12;
        diffuseColor.rgb+=diffuseColor.rgb*rib*.12;`);
    }
    sh.vertexShader='uniform float uGardenTime;\n'+sh.vertexShader;
    sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
      vec3 root=(instanceMatrix*vec4(0.,0.,0.,1.)).xyz;
      float gust=sin(uGardenTime*.66+root.x*.34+root.z*.23)*.65+sin(uGardenTime*1.7+root.x*1.4)*.35;
      float stem=clamp(position.y,0.,1.);
      transformed.x+=gust*stem*stem*${strength.toFixed(3)};
      transformed.z+=cos(uGardenTime*.84+root.z*.83)*stem*${(strength*.45).toFixed(3)};
      ${leaf ? `
      /* broad gusts arrive together, with a smaller out-of-phase flutter at
         each leaf tip. the shared clock also freezes both for reduced motion. */
      float flutter=sin(uGardenTime*5.1+root.x*3.7+root.z*4.3);
      float flutter2=sin(uGardenTime*3.8+root.y*5.2-root.z*2.1);
      transformed.z+=(flutter*.12+flutter2*.045)*( .65+.35*gust)*stem*stem;
      transformed.x+=flutter2*.045*stem;` : ''}`);
  };
  mat.customProgramCacheKey=()=> 'garden-wind-'+strength+'-'+leaf;
  return mat;
}
function buildGardenMaple(seed,x,z,scale,background=false) {
  const rnd=mulberry32(seed),parts=[],tips=[],up=new THREE.Vector3(0,1,0);
  const matrix=new THREE.Matrix4(),quat=new THREE.Quaternion();
  function limb(a,b,r0,r1){
    const d=b.clone().sub(a),length=d.length();
    const geo=new THREE.CylinderGeometry(r1,r0,length,background?5:9,1,true);
    quat.setFromUnitVectors(up,d.normalize());
    matrix.compose(a.clone().add(b).multiplyScalar(.5),quat,new THREE.Vector3(1,1,1));
    geo.applyMatrix4(matrix);parts.push(geo);
  }
  function branch(from,direction,length,radius,depth){
    const to=from.clone().addScaledVector(direction,length);
    const mid=from.clone().lerp(to,.5);mid.y-=length*.08;
    mid.x+=(rnd()-.5)*length*.13;
    limb(from,mid,radius,radius*.82);limb(mid,to,radius*.82,radius*.61);
    if(depth===3){tips.push(to);return;}
    for(let i=0;i<(depth===0?3:2);i++){
      const d=direction.clone();d.x+=(rnd()-.5)*1.25;d.z+=(rnd()-.5)*1.25;
      d.y=d.y*.57+.12+rnd()*.22;d.normalize();
      branch(to,d,length*(.63+rnd()*.12),radius*.62,depth+1);
    }
  }
  limb(new THREE.Vector3(),new THREE.Vector3(.12,1.45,-.04),.39,.27);
  limb(new THREE.Vector3(.12,1.45,-.04),new THREE.Vector3(-.10,2.5,.10),.27,.21);
  for(let i=0;i<6;i++){
    const a=i/6*TAU+rnd()*.6;
    branch(new THREE.Vector3(-.10,2.2+i*.11,.10),new THREE.Vector3(Math.cos(a)*.82,.65+rnd()*.25,Math.sin(a)*.82).normalize(),2.25+rnd()*.3,.17,0);
  }
  /* buttress roots meet the soil; the crown never has to carry a floating pole. */
  for(let i=0;i<6;i++){
    const a=i/6*TAU;
    limb(new THREE.Vector3(.03,.38,0),new THREE.Vector3(Math.cos(a)*.85,.01,Math.sin(a)*.85),.18,.028);
  }
  const trunk=new THREE.Mesh(mergeGeos(parts),GARDEN.bark);trunk.castShadow=true;trunk.receiveShadow=true;
  const count=tips.length*(background?9:(LOW?16:30));
  const leaves=new THREE.InstancedMesh(GARDEN.leafGeo,GARDEN.leafMat,count);
  const color=new THREE.Color(),p=new THREE.Vector3(),q=new THREE.Quaternion(),sc=new THREE.Vector3();
  for(let i=0;i<count;i++){
    const tip=tips[Math.floor(i/(count/tips.length))],a=rnd()*TAU,v=rnd()*2-1,r=Math.cbrt(rnd());
    p.set(tip.x+Math.cos(a)*Math.sqrt(1-v*v)*r*1.12,tip.y+v*r*.78,tip.z+Math.sin(a)*Math.sqrt(1-v*v)*r*1.12);
    q.setFromEuler(new THREE.Euler((rnd()-.5)*2.4,rnd()*TAU,(rnd()-.5)*2.4));
    const size=.23+rnd()*.20;sc.set(size,size,size);matrix.compose(p,q,sc);leaves.setMatrixAt(i,matrix);
    color.setHSL(GARDEN_STYLE==='forest'?.27+rnd()*.045:.995+rnd()*.019,GARDEN_STYLE==='forest'?.40+rnd()*.14:.82+rnd()*.12,GARDEN_STYLE==='forest'?.12+rnd()*.06:.105+rnd()*.065);leaves.setColorAt(i,color);
  }
  leaves.instanceMatrix.needsUpdate=true;leaves.instanceColor.needsUpdate=true;leaves.frustumCulled=false;
  const tree=new THREE.Group();tree.name=GARDEN_STYLE==='forest'?(background?'distant woodland tree':'woodland tree'):(background?'distant maple':'garden maple');tree.add(trunk,leaves);
  tree.position.set(x,Math.max(0,gardenGround(x,z))-.04,z);tree.scale.set(scale*1.18,scale*1.38,scale*1.18);
  tree.rotation.y=rnd()*TAU;GARDEN.group.add(tree);
}
function gardenPlantGeo(fern) {
  const p=[],idx=[],colors=[];
  function blade(a,b,c,color){const n=p.length/3;p.push(...a,...b,...c);idx.push(n,n+1,n+2);for(let i=0;i<3;i++)colors.push(...color);}
  if(fern){
    for(let f=0;f<7;f++){
      const a=f/7*TAU,dx=Math.cos(a),dz=Math.sin(a);
      for(let j=1;j<10;j++){
        const t=j/10,r=t*.78,y=Math.sin(t*2.5)*.56;
        const length=Math.sin(Math.PI*t)*.19;
        for(const side of [-1,1]){
          const root=[dx*r,y,dz*r],tip=[dx*(r+.065)-dz*length*side,y+.025,dz*(r+.065)+dx*length*side];
          blade(root,tip,[dx*(r+.095),y-.016,dz*(r+.095)],[.62+t*.20,.72+t*.25,.43+t*.12]);
        }
      }
    }
  }else{
    for(let j=0;j<7;j++){
      const a=j*2.4,h=.48+(j%3)*.16,dx=Math.cos(a),dz=Math.sin(a),w=.028;
      const left=[-dz*w,0,dx*w],right=[dz*w,0,-dx*w];
      const ml=[dx*.12-dz*w*.6,h*.6,dz*.12+dx*w*.6],mr=[dx*.12+dz*w*.6,h*.6,dz*.12-dx*w*.6];
      blade(left,right,ml,[.48,.64,.32]);blade(right,mr,ml,[.58,.73,.39]);
      blade(ml,mr,[dx*.34,h,dz*.34],[.72,.84,.47]);
    }
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));g.setIndex(idx);g.computeVertexNormals();return g;
}
function plantGardenBanks() {
  const rnd=mulberry32(93051),matrix=new THREE.Matrix4(),q=new THREE.Quaternion(),up=new THREE.Vector3(0,1,0),color=new THREE.Color();
  const mat=gardenWind(new THREE.MeshStandardMaterial({color:0x82965a,vertexColors:true,side:THREE.DoubleSide,roughness:.89,envMapIntensity:.8}),.24);
  const grass=new THREE.InstancedMesh(gardenPlantGeo(false),mat,LOW?1400:4500);
  const fern=new THREE.InstancedMesh(gardenPlantGeo(true),mat,LOW?(GARDEN_STYLE==='temple'?100:190):(GARDEN_STYLE==='temple'?300:580));
  const clumps=noise2D(119);
  for(const mesh of [grass,fern]){
    let count=0;
    for(let attempt=0;attempt<mesh.count*12 && count<mesh.count;attempt++){
      const bank=GARDEN_BANKS[attempt%GARDEN_BANKS.length],a=rnd()*TAU,r=Math.sqrt(rnd())*.92;
      const x=bank[0]+Math.cos(a)*bank[2]*r,z=bank[1]+Math.sin(a)*bank[3]*r,y=gardenGround(x,z);
      if(y<.06 || Math.abs(x)<5.6 || (mesh===fern&&r>.76))continue;
      if(mesh===grass && clumps(x*.7,z*.7)<-.15)continue;
      q.setFromAxisAngle(up,rnd()*TAU);const size=(mesh===fern?.55:.32)+rnd()*(mesh===fern?.65:.48);
      matrix.compose(new THREE.Vector3(x,y-.02,z),q,new THREE.Vector3(size,size*(.72+rnd()*.5),size));mesh.setMatrixAt(count,matrix);
      color.setHSL(.19+rnd()*.07,.24+rnd()*.15,.38+rnd()*.17);mesh.setColorAt(count,color);count++;
    }
    mesh.count=count;mesh.instanceMatrix.needsUpdate=true;mesh.instanceColor.needsUpdate=true;
    mesh.frustumCulled=false;mesh.receiveShadow=true;mesh.name=mesh===fern?'bank ferns':'bank sedges';GARDEN.group.add(mesh);
  }
}
function buildGardenTerrain() {
  const earth=gardenSurface(new THREE.MeshStandardMaterial({color:0x303323,roughness:.91,envMapIntensity:.65}), 'soil');
  GARDEN_BANKS.forEach(bank=>{
    const g=new THREE.PlaneGeometry(bank[2]*2.1,bank[3]*2.1,LOW?18:32,LOW?22:40);g.rotateX(-Math.PI/2);
    const p=g.attributes.position;
    for(let i=0;i<p.count;i++){const x=p.getX(i)+bank[0],z=p.getZ(i)+bank[1];p.setXYZ(i,x,gardenBankHeight(bank,x,z),z);}
    g.computeVertexNormals();const m=new THREE.Mesh(g,earth);m.receiveShadow=true;m.name='soft planted bank';GARDEN.group.add(m);
  });
  const stone=gardenSurface(new THREE.MeshStandardMaterial({color:0x4f554d,roughness:.81,envMapIntensity:.75}), 'stone');
  const geos=[0,1,2].map(i=>erodedRockGeo(1,3105+i*97,LOW?2:4));
  const rnd=mulberry32(93052),matrix=new THREE.Matrix4(),q=new THREE.Quaternion();
  const clusters=[[-7.3,5.8,1.5],[-10.7,1.7,1.15],[8.4,3.4,1.35],[12,-3.7,1.05],[-9.2,-6.3,1.0],[9.3,-10,1.1],[-12,-18,1.2],[13,-22,1.1]];
  geos.forEach((geo,type)=>{
    const mesh=new THREE.InstancedMesh(geo,stone,LOW?30:55);let count=0;
    for(let i=0;i<mesh.count;i++){
      const cluster=clusters[(i+type*3)%clusters.length],a=rnd()*TAU,r=rnd()*2.1;
      const x=cluster[0]+Math.cos(a)*r,z=cluster[1]+Math.sin(a)*r;
      const size=i<8?cluster[2]*(.70+rnd()*.4):.12+rnd()*.35;
      const y=gardenGround(x,z);
      q.setFromEuler(new THREE.Euler((rnd()-.5)*.22,rnd()*TAU,(rnd()-.5)*.15));
      matrix.compose(new THREE.Vector3(x,y+size*.23,z),q,new THREE.Vector3(size*(1+rnd()*.4),size*(.65+rnd()*.35),size));mesh.setMatrixAt(count++,matrix);
    }
    mesh.instanceMatrix.needsUpdate=true;mesh.castShadow=true;mesh.receiveShadow=true;mesh.name='weathered shoreline stones';GARDEN.group.add(mesh);
  });
  plantGardenBanks();
}
function gardenWaterMaterial(base) {
  const mat=base.clone(),compile=base.onBeforeCompile;
  mat.defines={...base.defines};
  mat.onBeforeCompile=sh=>{
    compile(sh);sh.uniforms.uGardenTime=WET_TIME;
    sh.fragmentShader='uniform float uGardenTime;\n'+sh.fragmentShader;
    sh.fragmentShader=sh.fragmentShader.replace('normal=normalize((viewMatrix*vec4(pondN,0.)).xyz);',`
      float calm=1.-smoothstep(1.5,8.,abs(vPondWorld.x));
      pondN.xz*=mix(.80,.28,calm);
      vec2 rp=vPondWorld.xz-vec2(-7.8,1.6);
      float rd=length(rp),pulse=mod(uGardenTime*.52,4.8);
      float ring=sin((rd-pulse)*29.)*exp(-pow((rd-pulse)*3.,2.))*exp(-rd*.42)*.007;
      pondN.xz+=normalize(rp+vec2(.001))*ring;
      normal=normalize((viewMatrix*vec4(pondN,0.)).xyz);`);
  };
  mat.customProgramCacheKey=()=> 'garden-pond-v1';return mat;
}
function buildGardenLeafRafts() {
  const rnd=mulberry32(93058),mat=new THREE.MeshStandardMaterial({color:0x743723,roughness:.57,side:THREE.DoubleSide});
  const leaves=new THREE.InstancedMesh(GARDEN.leafGeo,mat,LOW?24:60),matrix=new THREE.Matrix4(),q=new THREE.Quaternion();let count=0;
  for(let attempt=0;attempt<800 && count<leaves.count;attempt++){
    const side=rnd()>.5?1:-1,x=side*(6.5+rnd()*5),z=-4+rnd()*12;
    if(gardenGround(x,z)>-.18)continue;
    q.setFromEuler(new THREE.Euler(-Math.PI/2,0,rnd()*TAU));
    const size=.10+rnd()*.14;matrix.compose(new THREE.Vector3(x,.043,z),q,new THREE.Vector3(size,size,size));leaves.setMatrixAt(count++,matrix);
  }
  leaves.count=count;leaves.instanceMatrix.needsUpdate=true;leaves.layers.set(1);leaves.renderOrder=5;leaves.name='leaves gathered on water';GARDEN.group.add(leaves);
}
function buildGardenAtmosphere() {
  /* the existing cloud painting is retained. its moon now supplies the rim
     direction, with the old frontal key becoming a softer bounced fill. */
  const lights=scene.children.filter(o=>o.isDirectionalLight),rim=lights.find(o=>o!==WORLD.key);
  if(WORLD.key)gardenEdit(WORLD.key,'intensity',WORLD.key.intensity*.82);
  if(rim){
    gardenEdit(rim,'intensity',.46);
    const az=SKY.moonAzimuth*(1-.40*aspectFix()),el=SKY.moonElevation;
    const direction=new THREE.Vector3(Math.sin(az)*Math.cos(el),Math.sin(el),-Math.cos(az)*Math.cos(el));
    const position=rim.target.position.clone().addScaledVector(direction,75);
    for(const axis of ['x','y','z'])gardenEdit(rim.position,axis,position[axis]);
  }
  /* the old sampler chain produced no bloom. keep that visual baseline in
     the comparison, then let only the lit paper and wet peaks soften here. */
  if(typeof POST!=='undefined' && POST.comp && POST.bright){
    gardenEdit(POST.comp.uniforms.uBloom,'value',.46);
    gardenEdit(POST.bright.uniforms.uThr,'value',.42);
    gardenEdit(POST.bright.uniforms.uKnee,'value',.32);
  }
  gardenEdit(scene.fog,'density',scene.fog.density*.92);
  if(WORLD.studyStairMat){gardenEdit(WORLD.studyStairMat,'roughness',.72);gardenEdit(WORLD.studyStairMat,'envMapIntensity',.62);}
  if(WORLD.embers)GARDEN.original.push(WORLD.embers);
  WORLD.haze.forEach(h=>gardenEdit(h.material,'opacity',h.material.opacity*.65));
  const texture=tx(texGlow('rgba(150,175,182,.24)','rgba(95,125,137,.07)'));
  [[-12,.6,-8,14,1.6],[12,.8,-17,17,2.1],[-16,2,-31,24,3.2],[18,3,-47,31,5.0]].forEach((a,i)=>{
    const mat=new THREE.MeshBasicMaterial({map:texture,color:0x879aa8,transparent:true,opacity:.14,depthWrite:false,fog:true});
    const m=new THREE.Mesh(new THREE.PlaneGeometry(a[3],a[4]),mat);m.position.set(a[0],a[1],a[2]);m.name='low garden mist';m.renderOrder=5;
    mat.onBeforeCompile=sh=>{sh.uniforms.uGardenTime=WET_TIME;sh.vertexShader='uniform float uGardenTime;\n'+sh.vertexShader;
      sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>\ntransformed.x+=sin(uGardenTime*.09+${i.toFixed(1)})*.7;`);};
    GARDEN.group.add(m);
  });
}
function recordGardenFrame(raw) {
  if(!GARDEN.stats || raw>.25)return;
  GARDEN.frames++;GARDEN.elapsed+=raw;
  if(GARDEN.elapsed>2){
    GARDEN.stats.textContent=Math.round(GARDEN.frames/GARDEN.elapsed)+' fps · '+renderer.domElement.width+' × '+renderer.domElement.height+' px';
    GARDEN.frames=0;GARDEN.elapsed=0;
  }
}
function buildLandscapeStudy() {
  GARDEN.group=new THREE.Group();GARDEN.group.name='complete garden study';scene.add(GARDEN.group);
  /* keep the original grass framing and its scroll fade in every mode.
     only the old rock and overhead cutouts give way to the modeled garden. */
  GARDEN.original.push(...WORLD.fg.filter(o=>!/^grass(Far|Mid|Near)$/.test(o.name)));
  GARDEN.bark=gardenSurface(new THREE.MeshStandardMaterial({color:0x292720,roughness:.94,envMapIntensity:.65}), 'bark');
  /* the silhouette is geometry rather than a rectangular alpha sheet. */
  const leaf=new THREE.Shape();
  (GARDEN_STYLE==='temple'?[[0,0],[-.20,.19],[-.50,.25],[-.30,.39],[-.43,.63],[-.18,.55],[0,1],[.18,.55],[.43,.63],[.30,.39],[.50,.25],[.20,.19]]:[[0,0],[-.22,.20],[-.30,.46],[-.20,.72],[0,1],[.20,.72],[.30,.46],[.22,.20]]).forEach((p,i)=>i?leaf.lineTo(...p):leaf.moveTo(...p));leaf.closePath();
  GARDEN.leafGeo=new THREE.ShapeGeometry(leaf);
  const lp=GARDEN.leafGeo.attributes.position;
  for(let i=0;i<lp.count;i++)lp.setZ(i,Math.abs(lp.getX(i))*.18+Math.sin(lp.getY(i)*Math.PI)*.055);
  GARDEN.leafGeo.computeVertexNormals();
  GARDEN.leafMat=gardenWind(new THREE.MeshStandardMaterial({color:0xffffff,side:THREE.DoubleSide,roughness:.83,envMapIntensity:.78}),.20,true);
  if(GARDEN_STYLE==='temple'){gardenSway(GARDEN.bark,1,7,.10);gardenSway(GARDEN.leafMat,1,7,.10);}
  buildGardenTerrain();
  if(GARDEN_STYLE==='redwoods')buildGardenRedwoods();
  else if(GARDEN_STYLE==='forest')buildPondGarden();
  else {
    GARDEN.trees.forEach(args=>buildGardenMaple(...args));
    [[811,-22,-34,1.55],[812,23,-38,1.7],[813,-28,-52,1.95],[814,28,-58,2.15]].forEach(args=>buildGardenMaple(...args,true));

  }
  if(typeof buildGardenStonework==='function')buildGardenStonework();
  refineGardenGate();
  if(GARDEN_STYLE==='forest')addPondFlowersAndShore();
  if(GARDEN_STYLE==='redwoods')buildWoodlandUnderstory();
  buildGardenAtmosphere();
  buildGardenLeafRafts();
  gardenEdit(WORLD.pond,'material',gardenWaterMaterial(WORLD.pond.material));
  if(typeof qs==='function' && qs('studyStats','0')==='1' && document.querySelector('.study-controls')){
    GARDEN.stats=document.createElement('output');GARDEN.stats.id='study-performance';GARDEN.stats.className='study-status';
    GARDEN.stats.textContent='Measuring…';document.querySelector('.study-controls').appendChild(GARDEN.stats);
  }
  /* the old foreground updates its own visibility every frame. a parent
     switch keeps those cutouts hidden without changing their original fade. */
  GARDEN.originalGroup=new THREE.Group();GARDEN.originalGroup.name='original garden';
  GARDEN.original.forEach(o=>GARDEN.originalGroup.add(o));scene.add(GARDEN.originalGroup);
  GARDEN.ready=true;setGardenStudy(TEMPLE_STUDY.landscape);
}
