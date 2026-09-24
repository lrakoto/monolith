/* the near water stays open; taller bank shrubs lead to terrace trees
   and a loose canopy behind the hall instead of enclosing the basin. */
function gardenSway(mat, low, high, amount) {
  const compile=mat.onBeforeCompile,key=mat.customProgramCacheKey();
  mat.onBeforeCompile=sh=>{
    compile(sh);sh.uniforms.uGardenSway=WET_TIME;
    sh.vertexShader='uniform float uGardenSway;\n'+sh.vertexShader;
    sh.vertexShader=sh.vertexShader.replace('#include <project_vertex>',`
      vec4 mvPosition=vec4(transformed,1.);
      #ifdef USE_INSTANCING
        mvPosition=instanceMatrix*mvPosition;
      #endif
      float swayHeight=smoothstep(${low.toFixed(2)},${high.toFixed(2)},mvPosition.y);
      float breeze=sin(uGardenSway*.71+mvPosition.x*.12+mvPosition.z*.09)
        +.24*sin(uGardenSway*1.19+mvPosition.z*.25);
      mvPosition.x+=breeze*swayHeight*${amount.toFixed(3)};
      mvPosition.z+=sin(uGardenSway*.53+mvPosition.x*.16)*swayHeight*${(amount*.38).toFixed(3)};
      mvPosition=modelViewMatrix*mvPosition;
      gl_Position=projectionMatrix*mvPosition;`);
  };
  mat.customProgramCacheKey=()=>key+'-sway-'+low+'-'+high+'-'+amount;
  return mat;
}
function buildPondGarden() {
  const rnd=mulberry32(305481),matrix=new THREE.Matrix4(),q=new THREE.Quaternion(),up=new THREE.Vector3(0,1,0),color=new THREE.Color();
  const shrubs=[[-10.2,2.6,1.3],[11.8,1.4,1.5],[-13,-8,1.7],[14,-10,1.6],[-11,-18,2.9],[12,-21,3.2],[-15,-23,3.5],[16,-26,3.0],[-19,-30,3.3],[20,-32,2.8]];
  const twigs=[],locations=[];
  shrubs.forEach(([x,z,height])=>{
    const ground=Math.max(0,gardenGround(x,z));
    for(let branch=0;branch<7;branch++){
      const angle=rnd()*TAU,reach=(.5+rnd()*.8)*Math.max(1,height*.48);
      const start=new THREE.Vector3(x,ground-.03,z),end=new THREE.Vector3(x+Math.cos(angle)*reach,ground+height*(.55+rnd()*.45),z+Math.sin(angle)*reach);
      const d=end.clone().sub(start),g=new THREE.CylinderGeometry(.012,.045,d.length(),5,1,true);
      q.setFromUnitVectors(up,d.clone().normalize());g.applyQuaternion(q).translate(...start.clone().lerp(end,.5).toArray());twigs.push(g);
      for(let j=0;j<(LOW?18:42);j++){
        const a=rnd()*TAU,r=Math.sqrt(rnd())*.68*Math.max(1,height*.43);
        locations.push(new THREE.Vector3(end.x+Math.cos(a)*r,end.y+(rnd()-.5)*Math.max(.6,height*.33),end.z+Math.sin(a)*r));
      }
    }
  });
  const wood=new THREE.Mesh(mergeGeos(twigs),gardenSway(GARDEN.bark.clone(),.15,3.8,.12));wood.name='pond bank shrub branches';wood.receiveShadow=true;GARDEN.group.add(wood);
  const leafMat=gardenSway(gardenWind(new THREE.MeshStandardMaterial({color:0x93ac6d,side:THREE.DoubleSide,roughness:.82,envMapIntensity:.7}),.24,true),.15,3.8,.12);
  const leaves=new THREE.InstancedMesh(GARDEN.leafGeo,leafMat,locations.length);
  locations.forEach((p,i)=>{
    q.setFromEuler(new THREE.Euler((rnd()-.5)*1.7,rnd()*TAU,(rnd()-.5)*2));
    const size=.22+rnd()*.23;matrix.compose(p,q,new THREE.Vector3(size,size*1.3,size));leaves.setMatrixAt(i,matrix);
    color.setHSL(.24+rnd()*.07,.34+rnd()*.16,.22+rnd()*.12);leaves.setColorAt(i,color);
  });
  leaves.name='pond shrub leaves';leaves.frustumCulled=false;leaves.receiveShadow=true;GARDEN.group.add(leaves);

  /* use temple's familiar maple silhouettes, swapping left and right while
     preserving each tree's seed, size and depth. shrubs keep their oval leaves. */
  [[71,12.6,-13,1.05],[72,-11.8,-9.4,.95],[73,9.2,-19,.82],
   [74,-14.5,-17.5,1],[75,16.5,-6,.88]].forEach(([seed,x,z,size])=>buildGardenMaple(seed,-x,z,size));
  [[811,-22,-34,1.55],[812,23,-38,1.7],[813,-28,-52,1.95],
   [814,28,-58,2.15]].forEach(([seed,x,z,size])=>buildGardenMaple(seed,-x,z,size,true));

  const reedParts=[];
  for(let i=0;i<7;i++){
    const a=i/7*TAU,h=.95+(i%3)*.23,g=new THREE.PlaneGeometry(.075,h,1,7),p=g.attributes.position;
    for(let n=0;n<p.count;n++){
      const t=(p.getY(n)+h/2)/h;
      p.setXYZ(n,p.getX(n)*(1-t*.92)+Math.cos(a)*t*t*.38,t*h,Math.sin(a)*t*t*.38);
    }
    g.computeVertexNormals();reedParts.push(g);
  }
  const reedMat=gardenWind(new THREE.MeshStandardMaterial({color:0x536b32,roughness:.85,side:THREE.DoubleSide,envMapIntensity:.7}),.32);
  const reeds=new THREE.InstancedMesh(mergeGeos(reedParts),reedMat,LOW?100:260);
  let count=0;
  for(let i=0;i<4000 && count<reeds.count;i++){
    const side=i%2?1:-1,x=side*(6.7+rnd()*8),z=-15+rnd()*24,ground=gardenGround(x,z);
    if(ground<-.72 || ground>-.06)continue;
    const size=.75+rnd()*.55;
    q.setFromAxisAngle(up,rnd()*TAU);matrix.compose(new THREE.Vector3(x,ground-.02,z),q,new THREE.Vector3(size,size,size));reeds.setMatrixAt(count++,matrix);
  }
  reeds.count=count;reeds.name='emergent pond reeds';reeds.receiveShadow=true;reeds.frustumCulled=false;GARDEN.group.add(reeds);

  const pad=new THREE.Shape();pad.moveTo(0,0);
  for(let i=0;i<=22;i++){const a=.19+i/22*(TAU-.38);pad.lineTo(Math.cos(a),Math.sin(a));}pad.closePath();
  const padGeo=new THREE.ShapeGeometry(pad);padGeo.rotateX(-Math.PI/2);
  const padMat=new THREE.MeshStandardMaterial({color:0x375537,roughness:.45,side:THREE.DoubleSide,envMapIntensity:.8});
  padMat.onBeforeCompile=sh=>{sh.uniforms.uPadTime=WET_TIME;sh.vertexShader='uniform float uPadTime;\n'+sh.vertexShader;
    sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
      vec3 root=instanceMatrix[3].xyz;
      transformed.y+=sin(uPadTime*.75+root.x*.7+root.z)*.009;
      transformed.y+=position.x*sin(uPadTime*.63+root.z*.4)*.013;`);};
  padMat.customProgramCacheKey=()=> 'pond-pad-rocking-1';
  const pads=new THREE.InstancedMesh(padGeo,padMat,LOW?25:65);count=0;
  const colonies=[[-7.8,5.0],[8.1,4.6],[-8.8,-3.5],[9,-8.7]];
  for(let i=0;i<1500 && count<pads.count;i++){
    const c=colonies[i%colonies.length],a=rnd()*TAU,r=Math.sqrt(rnd())*1.7,x=c[0]+Math.cos(a)*r,z=c[1]+Math.sin(a)*r;
    if(Math.abs(x)<6.2 || gardenGround(x,z)>-.30)continue;
    q.setFromAxisAngle(up,rnd()*TAU);const size=.20+rnd()*.26;
    matrix.compose(new THREE.Vector3(x,.07,z),q,new THREE.Vector3(size,1,size*.85));pads.setMatrixAt(count,matrix);
    color.setHSL(.26+rnd()*.065,.28+rnd()*.14,.36+rnd()*.12);pads.setColorAt(count++,color);
  }
  buildPondAnimal();
  pads.count=count;pads.name='pond lily pads';pads.layers.set(1);pads.renderOrder=5;pads.frustumCulled=false;GARDEN.group.add(pads);
}
